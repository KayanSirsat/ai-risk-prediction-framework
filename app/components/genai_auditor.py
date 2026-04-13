import streamlit as st
import re
import time
import os
import requests
from dotenv import load_dotenv

load_dotenv()

NVIDIA_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL_NAME = "qwen/qwen3.5-122b-a10b"
API_KEY = os.getenv("NVIDIA_API_KEY")

MAX_RETRIES = 3
INITIAL_WAIT = 5
TIMEOUT = 180
MITIGATION_TTL = 600


def _call_nvidia_api(ticket_details, risk_level, shap_drivers):
    prompt = (
        f"You are an Agile Project Management Expert. "
        f"A Jira ticket has been flagged as {risk_level} Risk. "
        f"The top SHAP drivers are: {shap_drivers}. "
        f"The ticket details are: {ticket_details}. "
        f"You MUST format your exact response using these XML tags:\n"
        f"<reasoning>\n"
        f"[Your step-by-step analysis of the SHAP metrics]\n"
        f"</reasoning>\n"
        f"<strategy>\n"
        f"[Your concrete 3-step mitigation plan]\n"
        f"</strategy>"
    )

    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2048,
        "stream": False,
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    raw_content = ""
    wait_time = INITIAL_WAIT

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(
                NVIDIA_API_URL, json=payload, headers=headers, timeout=TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            raw_content = data["choices"][0]["message"].get("content", "")
            break
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            if attempt < MAX_RETRIES:
                print(
                    f"[WARNING] NVIDIA API timed out. Retrying in {wait_time} seconds (Attempt {attempt}/{MAX_RETRIES})..."
                )
                time.sleep(wait_time)
                wait_time *= 2
            else:
                print(
                    f"[ERROR] NVIDIA API unresponsive after {MAX_RETRIES} attempts. Giving up."
                )
                return {
                    "reasoning_trace": "Error: NVIDIA API is currently unresponsive due to high server load.",
                    "final_strategy": "Please try generating the strategy again in a few minutes. Network connection timed out after multiple attempts.",
                }
        except requests.exceptions.RequestException as e:
            return {
                "reasoning_trace": f"NVIDIA API connection failed: {e}",
                "final_strategy": "Unable to generate mitigation strategy. Check your API key and internet connection.",
            }
        except (KeyError, IndexError) as e:
            return {
                "reasoning_trace": f"Unexpected API response format: {e}",
                "final_strategy": "Unable to parse mitigation strategy from API response.",
            }

    if not API_KEY:
        return {
            "reasoning_trace": "NVIDIA_API_KEY not found in .env file.",
            "final_strategy": "Unable to generate mitigation strategy. Add your NVIDIA API key to the .env file.",
        }

    reasoning_trace = ""
    final_strategy = ""

    reasoning_match = re.search(r"<reasoning>(.*?)</reasoning>", raw_content, re.DOTALL)
    if reasoning_match:
        reasoning_trace = reasoning_match.group(1).strip()

    strategy_match = re.search(r"<strategy>(.*?)</strategy>", raw_content, re.DOTALL)
    if strategy_match:
        final_strategy = strategy_match.group(1).strip()

    if not reasoning_trace and not final_strategy:
        final_strategy = raw_content.strip()

    return {
        "reasoning_trace": reasoning_trace,
        "final_strategy": final_strategy,
    }


def render_mitigation_engine(ticket_id, risk_level, shap_drivers):
    st.subheader("Qwen 3.5 Autonomous Auditor")

    if "mitigation_cache" not in st.session_state:
        st.session_state.mitigation_cache = {}

    cached_result = None
    if ticket_id in st.session_state.mitigation_cache:
        entry = st.session_state.mitigation_cache[ticket_id]
        if time.time() - entry["timestamp"] < MITIGATION_TTL:
            cached_result = entry["result"]
        else:
            del st.session_state.mitigation_cache[ticket_id]

    if cached_result:
        if cached_result["reasoning_trace"]:
            with st.expander("IEEE Audit Trace (Reasoning)", expanded=True):
                st.info(cached_result["reasoning_trace"])
        if cached_result["final_strategy"]:
            st.markdown("**Mitigation Strategy**")
            st.markdown(cached_result["final_strategy"])
        st.caption(f"Cached (expires in {MITIGATION_TTL // 60} min)")
    else:
        if st.button("Generate Mitigation Strategy", type="primary"):
            with st.spinner("Connecting to Qwen 3.5 for analysis..."):
                ticket_details = {
                    "summary": str(shap_drivers.get("summary", "N/A"))
                    if isinstance(shap_drivers, dict)
                    else "N/A",
                    "priority": str(shap_drivers.get("priority", "N/A"))
                    if isinstance(shap_drivers, dict)
                    else "N/A",
                    "assignee_seniority": str(
                        shap_drivers.get("assignee_seniority", "N/A")
                    )
                    if isinstance(shap_drivers, dict)
                    else "N/A",
                    "estimated_days": int(shap_drivers.get("estimated_days", 0))
                    if isinstance(shap_drivers, dict)
                    else 0,
                    "story_points": int(shap_drivers.get("story_points", 0))
                    if isinstance(shap_drivers, dict)
                    else 0,
                    "budget_allocated": float(shap_drivers.get("budget_allocated", 0))
                    if isinstance(shap_drivers, dict)
                    else 0,
                }

                result = _call_nvidia_api(
                    ticket_details=ticket_details,
                    risk_level=risk_level,
                    shap_drivers=shap_drivers.get("top_factors", [])
                    if isinstance(shap_drivers, dict)
                    else [],
                )

                st.session_state.mitigation_cache[ticket_id] = {
                    "result": result,
                    "timestamp": time.time(),
                }
                st.rerun()

        st.info(
            "Click the button above to generate an AI-powered mitigation plan for this ticket."
        )
