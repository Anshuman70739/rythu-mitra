"""Accessible channel adapters: deterministic demo chat and IVR menu.

These routes power a local working demonstration. They are not a live WhatsApp/SMS
connection; external providers must be configured and verified separately.
"""
from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from ..security import api_error, csrf_required, rate_limit
from ..services.weather import get_weather

bp = Blueprint("channels", __name__)

_MENU = {
    "en": (
        "Welcome to Rythu Mitra (DEMO). Reply with a number: "
        "1 Weather, 2 Crop help, 3 Market prices, 4 Government schemes, 5 Human help."
    ),
    "te": (
        "రైతు మిత్రకు స్వాగతం (డెమో). ఒక సంఖ్య పంపండి: "
        "1 వాతావరణం, 2 పంట సమస్య, 3 మార్కెట్ ధరలు, 4 ప్రభుత్వ పథకాలు, 5 నిపుణుల సహాయం."
    ),
}
_INVALID = {
    "en": "Please reply 1–5, or type MENU to see the options.",
    "te": "దయచేసి 1–5 పంపండి లేదా ఎంపికల కోసం MENU అని పంపండి.",
}


def _reply(message: str, language: str) -> dict:
    text = message.strip()
    normalized = text.casefold()
    lang = "te" if language == "te" else "en"
    if normalized in {"", "hi", "hello", "start", "menu", "help", "హాయ్", "నమస్కారం"}:
        answer = _MENU[lang]
        status = "DEMO"
        human = False
    elif normalized in {"1", "weather", "వాతావరణం"} or normalized.startswith("weather "):
        # A city can be supplied as "weather Hyderabad"; never invent weather.
        city = " ".join(text.split()[1:]) if len(text.split()) > 1 else ""
        if city:
            # Do not let process-global weather cache data from another app/test
            # configuration masquerade as configured live data.
            if not current_app.config.get("OPENWEATHER_API_KEY") and not current_app.config.get("DEMO_MODE"):
                return {
                    "success": True, "channel": "demo-chat", "language": lang,
                    "status": "UNAVAILABLE",
                    "answer": "Live weather is not configured. No current weather is available.",
                    "source": None, "updated_at": None, "requires_human": False, "demo": True,
                }
            weather = get_weather(city)
            if weather.get("success"):
                if weather.get("status") == "DEMO":
                    answer = ("DEMO ONLY — fictional weather for " + city +
                              ". Do not use it to make farm decisions.") if lang == "en" else (
                              "డెమో మాత్రమే — " + city + " కోసం కల్పిత వాతావరణ సమాచారం. వ్యవసాయ నిర్ణయాలకు ఉపయోగించవద్దు.")
                else:
                    answer = (f"{city}: {weather.get('temperature')}°C, humidity {weather.get('humidity')}%. "
                              f"Source: {weather.get('source_name') or 'provider'}; updated: "
                              f"{weather.get('server_fetched_at') or 'unknown'}.")
                status = weather.get("status", "UNAVAILABLE")
            else:
                answer = weather.get("error", "Weather is currently unavailable.")
                status = "UNAVAILABLE"
        else:
            answer = ("Send: weather Hyderabad. Live weather requires a configured provider key."
                      if lang == "en" else
                      "ఈ విధంగా పంపండి: weather Hyderabad. ప్రత్యక్ష వాతావరణానికి API కీ అవసరం.")
            status = "UNAVAILABLE"
        human = False
    elif normalized in {"2", "crop", "crop help", "పంట సమస్య"}:
        answer = ("Tell us the crop, growth stage, and visible symptoms. A photo-based disease name is unavailable "
                  "until the model's verified class labels are installed. Avoid applying chemicals based only on a guess; "
                  "contact a local agriculture officer/KVK for urgent crop damage." if lang == "en" else
                  "పంట పేరు, పెరుగుదల దశ, కనిపించే లక్షణాలు చెప్పండి. ధృవీకరించిన మోడల్ లేబుళ్లు లేకుండా వ్యాధి పేరు చెప్పలేము. "
                  "ఊహ ఆధారంగా రసాయనాలు వాడకండి; తీవ్రమైన నష్టానికి స్థానిక వ్యవసాయ అధికారిని సంప్రదించండి.")
        status = "DEMO"
        human = True
    elif normalized in {"3", "market", "markets", "market prices", "ధరలు"}:
        answer = ("Market prices are unavailable until the official data provider is configured. When enabled, "
                  "Rythu Mitra will show reported date, market, commodity, units and source; it will not invent prices."
                  if lang == "en" else
                  "అధికారిక డేటా ప్రొవైడర్ అమర్చే వరకు మార్కెట్ ధరలు అందుబాటులో లేవు. ధర, మార్కెట్, తేదీ, మూలం చూపిస్తాం; "
                  "కల్పిత ధరలు చూపించము.")
        status = "UNAVAILABLE"
        human = False
    elif normalized in {"4", "scheme", "schemes", "పథకాలు"}:
        answer = ("We can help prepare a document checklist, but this demo does not submit applications or confirm eligibility. "
                  "Verify details on https://www.myscheme.gov.in/ or with your local agriculture office."
                  if lang == "en" else
                  "పత్రాల జాబితా సిద్ధం చేయడంలో సహాయం చేస్తాం. ఈ డెమో దరఖాస్తు పంపదు లేదా అర్హతను నిర్ధారించదు. "
                  "వివరాలను https://www.myscheme.gov.in/ లేదా స్థానిక వ్యవసాయ కార్యాలయంలో ధృవీకరించండి.")
        status = "DEMO"
        human = False
    elif normalized in {"5", "expert", "human", "agent", "నిపుణుడు"}:
        answer = ("Human follow-up requested in this demo. No real agent has been notified."
                  if lang == "en" else
                  "ఈ డెమోలో మానవ సహాయం కోరబడింది. నిజమైన సిబ్బందికి సమాచారం పంపలేదు.")
        status = "DEMO"
        human = True
    else:
        answer = _INVALID[lang]
        status = "DEMO"
        human = False
    return {
        "success": True,
        "channel": "demo-chat",
        "language": lang,
        "status": status,
        "answer": answer,
        "source": "Rythu Mitra backend demo flow",
        "updated_at": None,
        "requires_human": human,
        "demo": True,
    }


@bp.post("/api/channels/demo-chat")
@csrf_required
@rate_limit(30, 60)
def demo_chat():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return api_error("Send a JSON object with message and optional language.")
    message = data.get("message")
    language = data.get("language", "en")
    if not isinstance(message, str) or not 1 <= len(message.strip()) <= 500:
        return api_error("message must contain 1 to 500 characters.")
    if language not in {"en", "te"}:
        return api_error("language must be 'en' or 'te'.")
    return jsonify(_reply(message, language))


@bp.post("/api/channels/ivr/demo")
@csrf_required
@rate_limit(30, 60)
def demo_ivr():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return api_error("Send a JSON object with digits and optional language.")
    digits = data.get("digits", "")
    language = data.get("language", "en")
    if not isinstance(digits, str) or len(digits) > 20:
        return api_error("digits must be a string of at most 20 characters.")
    if language not in {"en", "te"}:
        return api_error("language must be 'en' or 'te'.")
    result = _reply(digits, language)
    result["channel"] = "ivr-demo"
    result["input_mode"] = "DTMF-demo"
    result["note"] = "Simulated phone-menu response; no call was placed."
    return jsonify(result)
