from __future__ import annotations

import csv
import os
import site
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))

user_site_packages = site.getusersitepackages()
if user_site_packages not in sys.path:
    sys.path.append(user_site_packages)

if not getattr(sys, "frozen", False):
    local_pydeps = str(Path(__file__).with_name(".pydeps"))
    if local_pydeps not in sys.path:
        sys.path.insert(0, local_pydeps)

    qt_dll_candidates = [
        Path(local_pydeps) / "bin",
        Path(local_pydeps) / "PyQt6" / "Qt6" / "bin",
        Path(local_pydeps) / "PyQt6" / "Qt" / "bin",
        Path(local_pydeps) / "PySide6",
        Path(local_pydeps) / "shiboken6",
    ]
    for candidate in qt_dll_candidates:
        if candidate.exists():
            try:
                os.add_dll_directory(str(candidate))
            except (AttributeError, OSError):
                pass

try:
    from PyQt6.QtCore import Qt, QTimer
    from PyQt6.QtGui import QColor, QFont, QIcon, QKeySequence, QPalette, QShortcut
    from PyQt6.QtWidgets import (
        QApplication,
        QCheckBox,
        QComboBox,
        QDoubleSpinBox,
        QFrame,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QProgressBar,
        QScrollArea,
        QSizePolicy,
        QSpinBox,
        QStackedWidget,
        QVBoxLayout,
        QWidget,
    )
    QT_BINDING = "PyQt6"
    PYQT_AVAILABLE = True
except Exception:
    try:
        from PySide6.QtCore import Qt, QTimer
        from PySide6.QtGui import QColor, QFont, QIcon, QKeySequence, QPalette, QShortcut
        from PySide6.QtWidgets import (
            QApplication,
            QCheckBox,
            QComboBox,
            QDoubleSpinBox,
            QFrame,
            QGridLayout,
            QGroupBox,
            QHBoxLayout,
            QLabel,
            QLineEdit,
            QMainWindow,
            QMessageBox,
            QPushButton,
            QProgressBar,
            QScrollArea,
            QSizePolicy,
            QSpinBox,
            QStackedWidget,
            QVBoxLayout,
            QWidget,
        )
        QT_BINDING = "PySide6"
        PYQT_AVAILABLE = True
    except Exception:
        QT_BINDING = "None"
        PYQT_AVAILABLE = False
        class _QtNamespace:
            def __getattr__(self, _name: str) -> "_QtNamespace":
                return self

            def __call__(self, *args: Any, **kwargs: Any) -> "_QtNamespace":
                return self

        def _stub_class(_name: str) -> type:
            return type(_name, (), {})

        Qt = _QtNamespace()  # type: ignore[assignment]
        QTimer = _stub_class("QTimer")  # type: ignore[assignment]
        QColor = _stub_class("QColor")  # type: ignore[assignment]
        QFont = _stub_class("QFont")  # type: ignore[assignment]
        QIcon = _stub_class("QIcon")  # type: ignore[assignment]
        QKeySequence = _stub_class("QKeySequence")  # type: ignore[assignment]
        QPalette = _stub_class("QPalette")  # type: ignore[assignment]
        QShortcut = _stub_class("QShortcut")  # type: ignore[assignment]
        QApplication = _stub_class("QApplication")  # type: ignore[assignment]
        QCheckBox = _stub_class("QCheckBox")  # type: ignore[assignment]
        QComboBox = _stub_class("QComboBox")  # type: ignore[assignment]
        QDoubleSpinBox = _stub_class("QDoubleSpinBox")  # type: ignore[assignment]
        QFrame = _stub_class("QFrame")  # type: ignore[assignment]
        QGridLayout = _stub_class("QGridLayout")  # type: ignore[assignment]
        QGroupBox = _stub_class("QGroupBox")  # type: ignore[assignment]
        QHBoxLayout = _stub_class("QHBoxLayout")  # type: ignore[assignment]
        QLabel = _stub_class("QLabel")  # type: ignore[assignment]
        QLineEdit = _stub_class("QLineEdit")  # type: ignore[assignment]
        QMainWindow = _stub_class("QMainWindow")  # type: ignore[assignment]
        QMessageBox = _stub_class("QMessageBox")  # type: ignore[assignment]
        QPushButton = _stub_class("QPushButton")  # type: ignore[assignment]
        QProgressBar = _stub_class("QProgressBar")  # type: ignore[assignment]
        QScrollArea = _stub_class("QScrollArea")  # type: ignore[assignment]
        QSizePolicy = _stub_class("QSizePolicy")  # type: ignore[assignment]
        QSpinBox = _stub_class("QSpinBox")  # type: ignore[assignment]
        QStackedWidget = _stub_class("QStackedWidget")  # type: ignore[assignment]
        QVBoxLayout = _stub_class("QVBoxLayout")  # type: ignore[assignment]
        QWidget = _stub_class("QWidget")  # type: ignore[assignment]


APP_NAME = "SUSTAINABLE FLIGHT OPERATIONS — DSS DEMO"
LOG_FILE = BASE_DIR / "dss_decision_log.csv"
DEFAULT_WINDOW_WIDTH = 800
DEFAULT_WINDOW_HEIGHT = 600
APP_ICON_PATH = BASE_DIR / "assets" / "app.png"
SPIN_UP_ICON_PATH = BASE_DIR / "assets" / "spin_up.svg"
SPIN_DOWN_ICON_PATH = BASE_DIR / "assets" / "spin_down.svg"


def app_icon_path() -> Optional[str]:
    if APP_ICON_PATH.exists():
        return str(APP_ICON_PATH)
    return None


def stylesheet_asset_path(path: Path) -> str:
    return path.resolve().as_posix()


def verdict_visual(verdict_key: str) -> Dict[str, str]:
    visuals = {
        "RECOMMEND": {"icon": "✓", "accent": "#1f7a3d", "bg": "#eaf7ef", "border": "#b8e0c4"},
        "CONDITIONAL": {"icon": "◐", "accent": "#8a6400", "bg": "#fff7e6", "border": "#ead49c"},
        "DO_NOT_RECOMMEND": {"icon": "⛔", "accent": "#9b1027", "bg": "#fde8ea", "border": "#f2b3bc"},
        "SUPPRESSED": {"icon": "◌", "accent": "#666666", "bg": "#f0f0f0", "border": "#dddddd"},
    }
    return visuals.get(verdict_key, visuals["CONDITIONAL"])


def metric_icon(metric_key: str) -> str:
    return {
        "confidence": "✓",
        "fuel": "⛽",
        "co2": "♻",
        "applied": "✓",
        "summary": "✦",
    }.get(metric_key, "•")


class Verdict(Enum):
    RECOMMEND = "Recommended"
    CONDITIONAL = "Conditional"
    DO_NOT_RECOMMEND = "Not Recommended"
    SUPPRESSED = "System Silenced"


class PilotChoice(Enum):
    APPLIED = "Applied"
    NOT_SUITABLE = "Not Suitable"
    IGNORED = "Ignored"
    NO_LOG = "No Log"


BACK = object()


@dataclass
class FlightContext:
    flight_id: str = "DEMO001"
    aircraft_type: str = "A320"
    phase: str = "cruise"
    crew_workload: int = 2
    abnormal_situation: bool = False
    sop_compatible: bool = True
    delay_pressure: bool = False
    icing_conditions: bool = False
    turbulence_forecast: str = "none"
    low_visibility: bool = False
    crosswind_kt: float = 0.0
    tailwind_kt: float = 0.0
    runway_length_m: int = 3000
    braking_action: str = "good"
    runway_contaminated: bool = False
    landing_weight_high: bool = False
    atc_constraints: bool = False
    traffic_density_high: bool = False
    taxi_time_min: int = 10
    step_climb_savings_kg: float = 0.0


@dataclass
class Decision:
    name: str
    verdict: Verdict = Verdict.CONDITIONAL
    reasons: List[str] = field(default_factory=list)
    caveats: List[str] = field(default_factory=list)
    confidence: int = 0

    def render(self) -> str:
        symbol = {
            Verdict.RECOMMEND: "✅",
            Verdict.CONDITIONAL: "⚠️",
            Verdict.DO_NOT_RECOMMEND: "⛔",
            Verdict.SUPPRESSED: "🤫",
        }[self.verdict]

        out = f"\n{symbol} {self.name}: {self.verdict.value} (confidence: {self.confidence}%)"

        if self.reasons:
            out += "\n   Reasons:"
            for reason in self.reasons:
                out += f"\n     • {reason}"

        if self.caveats:
            out += "\n   Caveats / Conditions:"
            for caveat in self.caveats:
                out += f"\n     • {caveat}"

        out += "\n   ── Final decision always belongs to the pilot in command. ──"
        return out


@dataclass
class Question:
    key: str
    label: str
    kind: str
    default: Any
    section: str
    choices: List[str] = field(default_factory=list)
    minimum: Optional[float] = None
    maximum: Optional[float] = None
    hint: str = ""


QUESTIONS: List[Question] = [
    Question("flight_id", "Flight / scenario ID", "text", "DEMO001", "Identity & Phase"),
    Question("aircraft_type", "Aircraft type", "text", "A320", "Identity & Phase"),
    Question(
        "phase",
        "Flight phase",
        "choice",
        "cruise",
        "Identity & Phase",
        choices=["taxi", "takeoff", "climb", "cruise", "descent", "approach", "landing"],
    ),
    Question(
        "crew_workload",
        "Crew workload (1=low, 5=high)",
        "int",
        2,
        "Crew & Ops",
        minimum=1,
        maximum=5,
    ),
    Question("abnormal_situation", "Abnormal / non-normal situation active?", "bool", False, "Crew & Ops"),
    Question("sop_compatible", "Is the action SOP compliant?", "bool", True, "Crew & Ops"),
    Question("delay_pressure", "Is there delay / time pressure?", "bool", False, "Crew & Ops"),
    Question("icing_conditions", "Icing conditions present?", "bool", False, "Weather"),
    Question(
        "turbulence_forecast",
        "Turbulence forecast",
        "choice",
        "none",
        "Weather",
        choices=["none", "light", "moderate", "severe"],
    ),
    Question("low_visibility", "Low visibility present?", "bool", False, "Weather"),
    Question(
        "crosswind_kt",
        "Crosswind (kt)",
        "float",
        0.0,
        "Weather",
        minimum=0.0,
    ),
    Question(
        "tailwind_kt",
        "Tailwind (kt)",
        "float",
        0.0,
        "Weather",
        minimum=0.0,
    ),
    Question(
        "runway_length_m",
        "Runway length (m)",
        "int",
        3000,
        "Runway / Surface",
        minimum=500,
        maximum=6000,
    ),
    Question(
        "braking_action",
        "Braking action",
        "choice",
        "good",
        "Runway / Surface",
        choices=["good", "medium", "poor", "unknown"],
    ),
    Question("runway_contaminated", "Runway contaminated?", "bool", False, "Runway / Surface"),
    Question("landing_weight_high", "High landing weight?", "bool", False, "Runway / Surface"),
    Question("atc_constraints", "ATC constraints present?", "bool", False, "Traffic & ATC"),
    Question("traffic_density_high", "High traffic density?", "bool", False, "Traffic & ATC"),
    Question(
        "taxi_time_min",
        "Expected taxi time (min)",
        "int",
        10,
        "Taxi",
        minimum=0,
        maximum=90,
    ),
    Question(
        "step_climb_savings_kg",
        "Estimated step climb fuel savings (kg)",
        "float",
        0.0,
        "Step Climb",
        minimum=0.0,
    ),
]


def clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def banner(title: str) -> None:
    print("\n" + "═" * 80)
    print(f"  {title}")
    print("═" * 80)


def check_suppression(ctx: FlightContext) -> Optional[str]:
    if ctx.abnormal_situation:
        return "The system stays silent because an abnormal / non-normal situation is active."
    if ctx.crew_workload >= 5:
        return "The system stays silent to avoid distraction during very high crew workload."
    if ctx.turbulence_forecast == "severe":
        return "The system stays silent because severe turbulence is forecast."
    if ctx.low_visibility and ctx.phase in ("taxi", "takeoff", "approach", "landing"):
        return "The system stays silent due to low visibility in a critical flight phase."
    if not ctx.sop_compatible:
        return "The system stays silent because the action is not SOP compliant."
    return None


def evaluate_single_engine_taxi(ctx: FlightContext) -> Decision:
    d = Decision(name="Single Engine Taxi")
    if ctx.phase != "taxi":
        d.verdict = Verdict.SUPPRESSED
        d.reasons = [f"This decision can only be evaluated in the taxi phase. Current phase: {ctx.phase}"]
        return d

    reasons: List[str] = []
    caveats: List[str] = []
    confidence = 70

    if ctx.aircraft_type.upper().startswith("A320") and ctx.icing_conditions:
        d.verdict = Verdict.DO_NOT_RECOMMEND
        d.reasons = ["Single engine taxi is not recommended in icing conditions for A320 operations."]
        d.confidence = 95
        return d

    if ctx.taxi_time_min < 5:
        d.verdict = Verdict.DO_NOT_RECOMMEND
        reasons.append(f"Expected taxi time is {ctx.taxi_time_min} min; fuel savings would be limited.")
        confidence = 85
    elif ctx.taxi_time_min >= 10:
        d.verdict = Verdict.RECOMMEND
        reasons.append(
            f"Expected taxi time is {ctx.taxi_time_min} min; fuel and emissions savings are meaningful."
        )
        reasons.append("Reducing engine run time may also lower maintenance cost.")
        confidence = 85
    else:
        d.verdict = Verdict.CONDITIONAL
        reasons.append(
            f"Expected taxi time is {ctx.taxi_time_min} min; decision should be based on operational conditions."
        )
        confidence = 60

    if ctx.traffic_density_high:
        d.verdict = Verdict.CONDITIONAL
        caveats.append("High taxi traffic density may reduce maneuvering flexibility.")
        confidence = min(confidence, 65)

    if ctx.crew_workload >= 4:
        d.verdict = Verdict.CONDITIONAL
        caveats.append("High crew workload means the captain should make the final call.")
        confidence = min(confidence, 60)

    d.reasons, d.caveats, d.confidence = reasons, caveats, confidence
    return d


def evaluate_idle_reverse_thrust(ctx: FlightContext) -> Decision:
    d = Decision(name="Idle Reverse Thrust")
    if ctx.phase not in ("approach", "landing"):
        d.verdict = Verdict.SUPPRESSED
        d.reasons = [f"This decision can only be evaluated in the approach or landing phase. Current phase: {ctx.phase}"]
        return d

    reasons: List[str] = []
    caveats: List[str] = []
    confidence = 70

    if ctx.runway_contaminated or ctx.braking_action in ("poor", "unknown") or ctx.tailwind_kt > 10:
        d.verdict = Verdict.DO_NOT_RECOMMEND
        if ctx.tailwind_kt > 10:
            reasons.append(f"High tailwind detected ({ctx.tailwind_kt:.0f} kt). Full reverse is recommended.")
        else:
            reasons.append(f"Runway condition is not suitable or is uncertain. Braking action: {ctx.braking_action}.")
        reasons.append("Safety must be prioritized in this case.")
        d.reasons, d.confidence = reasons, 95
        return d

    if ctx.runway_length_m >= 2800 and ctx.braking_action == "good" and not ctx.landing_weight_high:
        d.verdict = Verdict.RECOMMEND
        reasons.append(
            f"Runway length is {ctx.runway_length_m}m and braking is good; idle reverse is efficient for fuel and maintenance."
        )
        confidence = 88
    elif ctx.runway_length_m < 2200:
        d.verdict = Verdict.DO_NOT_RECOMMEND
        reasons.append(
            f"Runway is short ({ctx.runway_length_m} m); higher reverse usage may provide a better safety margin."
        )
        confidence = 90
    else:
        d.verdict = Verdict.CONDITIONAL
        reasons.append(
            "Runway conditions are moderate; decision should depend on landing weight, braking performance, and company procedures."
        )
        confidence = 65

    if ctx.crosswind_kt >= 20:
        d.verdict = Verdict.CONDITIONAL
        caveats.append(
            f"Crosswind is {ctx.crosswind_kt:.0f} kt; post-landing control and directional handling require caution."
        )
        confidence = min(confidence, 65)

    d.reasons, d.caveats, d.confidence = reasons, caveats, confidence
    return d


def evaluate_step_climb(ctx: FlightContext) -> Decision:
    d = Decision(name="Step Climb / Altitude Optimization")
    if ctx.phase not in ("climb", "cruise"):
        d.verdict = Verdict.SUPPRESSED
        d.reasons = [f"This decision can only be evaluated in the climb or cruise phase. Current phase: {ctx.phase}"]
        return d

    reasons: List[str] = []
    caveats: List[str] = []
    confidence = 70

    if ctx.turbulence_forecast in ("moderate", "severe"):
        d.verdict = Verdict.DO_NOT_RECOMMEND
        d.reasons = [
            f"{ctx.turbulence_forecast.capitalize()} turbulence is forecast aloft; passenger comfort and safety take priority."
        ]
        d.confidence = 90
        return d

    if ctx.step_climb_savings_kg >= 150:
        d.verdict = Verdict.RECOMMEND
        reasons.append(f"Estimated fuel savings are {ctx.step_climb_savings_kg:.0f} kg; this is meaningful for sustainability.")
        confidence = 88
    elif ctx.step_climb_savings_kg >= 50:
        d.verdict = Verdict.CONDITIONAL
        reasons.append(
            f"Estimated fuel savings are {ctx.step_climb_savings_kg:.0f} kg; it can be considered based on ATC and traffic conditions."
        )
        confidence = 65
    else:
        d.verdict = Verdict.DO_NOT_RECOMMEND
        reasons.append(
            f"Estimated fuel savings are {ctx.step_climb_savings_kg:.0f} kg; it may not justify the operational workload."
        )
        confidence = 80

    if ctx.atc_constraints:
        if d.verdict == Verdict.RECOMMEND:
            d.verdict = Verdict.CONDITIONAL
        caveats.append("ATC restrictions are present; it cannot be applied without clearance.")
        confidence = min(confidence, 70)

    if ctx.traffic_density_high:
        caveats.append("Traffic density may limit step climb applicability.")

    if ctx.turbulence_forecast == "light":
        caveats.append("Light turbulence is forecast; passenger comfort should be considered.")

    d.reasons, d.caveats, d.confidence = reasons, caveats, confidence
    return d


DECISIONS = {
    "step_climb": evaluate_step_climb,
    "idle_reverse": evaluate_idle_reverse_thrust,
    "single_engine_taxi": evaluate_single_engine_taxi,
}

DECISION_LABELS = {
    "step_climb": "Step Climb / Altitude Optimization",
    "idle_reverse": "Idle Reverse Thrust",
    "single_engine_taxi": "Single Engine Taxi",
}


def fuel_saved_estimate(decision_key: str, ctx: FlightContext) -> float:
    if decision_key == "step_climb":
        return max(0.0, ctx.step_climb_savings_kg)
    if decision_key == "idle_reverse":
        return 15.0
    if decision_key == "single_engine_taxi":
        return max(0.0, float(ctx.taxi_time_min) * 5.0)
    return 0.0


def decision_impact_estimate(decision_key: str, ctx: FlightContext) -> Dict[str, float]:
    fuel_saved_kg = fuel_saved_estimate(decision_key, ctx)
    return {
        "fuel_saved_kg": fuel_saved_kg,
        "co2_prevented_kg": fuel_saved_kg * 3.16,
    }


def evaluate(decision_key: str, ctx: FlightContext) -> Decision:
    suppression_reason = check_suppression(ctx)
    label = DECISION_LABELS.get(decision_key, decision_key)

    if suppression_reason is not None:
        return Decision(name=label, verdict=Verdict.SUPPRESSED, reasons=[suppression_reason], confidence=100)

    fn = DECISIONS.get(decision_key)
    if fn is None:
        return Decision(name=label, verdict=Verdict.DO_NOT_RECOMMEND, reasons=[f"Unknown decision type: {decision_key}"], confidence=0)

    return fn(ctx)


def evaluate_all(ctx: FlightContext) -> List[Dict[str, Any]]:
    payloads: List[Dict[str, Any]] = []
    for key in DECISIONS:
        decision = evaluate(key, ctx)
        payloads.append(
            {
                "key": key,
                "name": decision.name,
                "verdict_key": decision.verdict.name,
                "verdict": decision.verdict.value,
                "symbol": {
                    Verdict.RECOMMEND: "✅",
                    Verdict.CONDITIONAL: "⚠️",
                    Verdict.DO_NOT_RECOMMEND: "⛔",
                    Verdict.SUPPRESSED: "🤫",
                }[decision.verdict],
                "reasons": decision.reasons,
                "caveats": decision.caveats,
                "confidence": decision.confidence,
                "suppressed": decision.verdict == Verdict.SUPPRESSED,
                "fuel_saved_kg_estimate": fuel_saved_estimate(key, ctx),
                "co2_prevented_kg_estimate": round(fuel_saved_estimate(key, ctx) * 3.16, 1),
            }
        )
    return payloads


def scenario_summary(decisions: List[Dict[str, Any]], ctx: FlightContext) -> Dict[str, Any]:
    recommended = sum(1 for item in decisions if item["verdict_key"] == Verdict.RECOMMEND.name)
    conditional = sum(1 for item in decisions if item["verdict_key"] == Verdict.CONDITIONAL.name)
    not_recommend = sum(1 for item in decisions if item["verdict_key"] == Verdict.DO_NOT_RECOMMEND.name)
    suppressed = sum(1 for item in decisions if item["verdict_key"] == Verdict.SUPPRESSED.name)
    active_confidences = [item["confidence"] for item in decisions if item["verdict_key"] != Verdict.SUPPRESSED.name]
    average_confidence = round(sum(active_confidences) / len(active_confidences)) if active_confidences else 0

    total_fuel = 0.0
    for item in decisions:
        if item["verdict_key"] == Verdict.SUPPRESSED.name:
            continue
        total_fuel += item["fuel_saved_kg_estimate"]

    return {
        "overall_state": "SYSTEM SILENCED" if suppressed == len(decisions) else "ACTIVE EVALUATION",
        "recommended": recommended,
        "conditional": conditional,
        "not_recommend": not_recommend,
        "suppressed": suppressed,
        "average_confidence": average_confidence,
        "decision_count": len(decisions),
        "estimated_fuel_kg": round(total_fuel),
        "estimated_co2_kg": round(total_fuel * 3.16, 1),
    }


def parse_context(payload: Dict[str, Any]) -> FlightContext:
    def as_int(name: str, default: int, lo: Optional[int] = None, hi: Optional[int] = None) -> int:
        raw = payload.get(name, default)
        try:
            value = int(float(raw))
        except (TypeError, ValueError):
            value = default
        if lo is not None:
            value = max(lo, value)
        if hi is not None:
            value = min(hi, value)
        return value

    def as_float(name: str, default: float, lo: Optional[float] = None, hi: Optional[float] = None) -> float:
        raw = payload.get(name, default)
        try:
            value = float(raw)
        except (TypeError, ValueError):
            value = default
        if lo is not None:
            value = max(lo, value)
        if hi is not None:
            value = min(hi, value)
        return value

    def as_bool(name: str, default: bool) -> bool:
        raw = payload.get(name, default)
        if isinstance(raw, bool):
            return raw
        if isinstance(raw, (int, float)):
            return bool(raw)
        if isinstance(raw, str):
            return raw.strip().lower() in {"1", "true", "yes", "on", "y"}
        return default

    def as_str(name: str, default: str) -> str:
        raw = payload.get(name, default)
        return default if raw is None else str(raw)

    return FlightContext(
        flight_id=as_str("flight_id", "DEMO001"),
        aircraft_type=as_str("aircraft_type", "A320"),
        phase=as_str("phase", "cruise"),
        crew_workload=as_int("crew_workload", 2, 1, 5),
        abnormal_situation=as_bool("abnormal_situation", False),
        sop_compatible=as_bool("sop_compatible", True),
        delay_pressure=as_bool("delay_pressure", False),
        icing_conditions=as_bool("icing_conditions", False),
        turbulence_forecast=as_str("turbulence_forecast", "none"),
        low_visibility=as_bool("low_visibility", False),
        crosswind_kt=as_float("crosswind_kt", 0.0, 0.0),
        tailwind_kt=as_float("tailwind_kt", 0.0, 0.0),
        runway_length_m=as_int("runway_length_m", 3000, 500, 6000),
        braking_action=as_str("braking_action", "good"),
        runway_contaminated=as_bool("runway_contaminated", False),
        landing_weight_high=as_bool("landing_weight_high", False),
        atc_constraints=as_bool("atc_constraints", False),
        traffic_density_high=as_bool("traffic_density_high", False),
        taxi_time_min=as_int("taxi_time_min", 10, 0, 90),
        step_climb_savings_kg=as_float("step_climb_savings_kg", 0.0, 0.0),
    )


def value_text(question: Question, value: Any) -> str:
    if question.kind == "bool":
        return "Yes" if value else "No"
    return str(value)


def parse_answer(question: Question, raw: str, current_value: Any = None) -> Any:
    cleaned = raw.strip()
    if cleaned == "":
        return question.default if current_value is None else current_value

    lowered = cleaned.lower()
    if lowered in {"back"}:
        return BACK
    if lowered in {"next", "forward"}:
        return question.default if current_value is None else current_value
    if lowered in {"quit", "exit", "q"}:
        raise KeyboardInterrupt

    if question.kind == "bool":
        truthy = {"y", "yes", "true", "1", "on"}
        falsy = {"n", "no", "false", "0", "off"}
        if lowered in truthy:
            return True
        if lowered in falsy:
            return False
        raise ValueError("Expected Yes/No (Y/N).")

    if question.kind == "int":
        value = int(cleaned)
        if question.minimum is not None and value < question.minimum:
            raise ValueError(f"Minimum allowed is {question.minimum}.")
        if question.maximum is not None and value > question.maximum:
            raise ValueError(f"Maximum allowed is {question.maximum}.")
        return value

    if question.kind == "float":
        value = float(cleaned.replace(",", "."))
        if question.minimum is not None and value < question.minimum:
            raise ValueError(f"Minimum allowed is {question.minimum}.")
        if question.maximum is not None and value > question.maximum:
            raise ValueError(f"Maximum allowed is {question.maximum}.")
        return value

    if question.kind == "choice":
        if cleaned.isdigit():
            index = int(cleaned) - 1
            if 0 <= index < len(question.choices):
                return question.choices[index]
        for choice in question.choices:
            if choice.lower() == lowered:
                return choice
        raise ValueError(f"Options: {', '.join(question.choices)}")

    return cleaned


def question_prompt(question: Question, index: int, total: int, current_value: Any) -> None:
    banner(f"QUESTION {index + 1}/{total} — {question.section}")
    print(f"{question.label}")
    if question.hint:
        print(f"  {question.hint}")
    if question.kind == "choice":
        print("  Options:")
        for pos, choice in enumerate(question.choices, start=1):
            print(f"    {pos}. {choice}")
    print(f"  Current: {value_text(question, current_value)}")
    print("  Commands: Enter=default, back=previous, quit=cancel")


def ask_questions() -> Optional[FlightContext]:
    answers: Dict[str, Any] = {question.key: question.default for question in QUESTIONS}
    index = 0
    total = len(QUESTIONS)

    while 0 <= index < total:
        question = QUESTIONS[index]
        current_value = answers.get(question.key, question.default)
        clear_screen()
        print(APP_NAME)
        question_prompt(question, index, total, current_value)

        try:
            raw = input("\nAnswer: ")
            parsed = parse_answer(question, raw, current_value)
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            return None
        except ValueError as exc:
            print(f"\n  ! {exc}")
            input("  Press Enter to continue...")
            continue

        if parsed is BACK:
            if index == 0:
                print("\n  ! You are at the first question.")
                input("  Press Enter to continue...")
                continue
            index -= 1
            continue

        answers[question.key] = parsed
        index += 1

    return parse_context(answers)


def print_context_review(ctx: FlightContext) -> None:
    banner("ENTERED CONTEXT")
    groups = [
        ("Identity & Phase", ["flight_id", "aircraft_type", "phase"]),
        ("Crew & Ops", ["crew_workload", "abnormal_situation", "sop_compatible", "delay_pressure"]),
        ("Weather", ["icing_conditions", "turbulence_forecast", "low_visibility", "crosswind_kt", "tailwind_kt"]),
        ("Runway / Surface", ["runway_length_m", "braking_action", "runway_contaminated", "landing_weight_high"]),
        ("Traffic & ATC", ["atc_constraints", "traffic_density_high"]),
        ("Taxi", ["taxi_time_min"]),
        ("Step Climb", ["step_climb_savings_kg"]),
    ]
    values = asdict(ctx)
    for title, keys in groups:
        print(f"\n[{title}]")
        for key in keys:
            print(f"  - {key}: {values[key]}")
    print()


def ask_review_action() -> str:
    print("Options:")
    print("  e  - Evaluate")
    print("  b  - Go back to last question")
    print("  j  - Jump to a specific question")
    print("  q  - Quit")
    raw = input("\nChoice: ").strip().lower()
    return raw


def show_decision_screen(ctx: FlightContext, decisions: List[Dict[str, Any]]) -> None:
    clear_screen()
    banner("EVALUATION RESULT")
    print(f"Flight ID: {ctx.flight_id}   Aircraft: {ctx.aircraft_type}   Phase: {ctx.phase}")
    print(
        f"Summary: {sum(1 for d in decisions if d['verdict_key'] == Verdict.RECOMMEND.name)} recommendations, "
        f"{sum(1 for d in decisions if d['verdict_key'] == Verdict.CONDITIONAL.name)} conditional, "
        f"{sum(1 for d in decisions if d['verdict_key'] == Verdict.DO_NOT_RECOMMEND.name)} not recommended, "
        f"{sum(1 for d in decisions if d['verdict_key'] == Verdict.SUPPRESSED.name)} silent"
    )

    for item in decisions:
        d = Decision(
            name=item["name"],
            verdict=Verdict[item["verdict_key"]],
            reasons=item["reasons"],
            caveats=item["caveats"],
            confidence=item["confidence"],
        )
        print(d.render())

    summary = scenario_summary(decisions, ctx)
    print("\n" + "─" * 80)
    print("POST-FLIGHT DEBRIEF")
    print(f"  Total estimated fuel savings : {summary['estimated_fuel_kg']} kg")
    print(f"  Prevented CO2 emissions      : {summary['estimated_co2_kg']} kg")
    print(f"  Average confidence           : {summary['average_confidence']}%")
    print("─" * 80)


def generate_sustainability_debrief(ctx: FlightContext, applied_decisions: List[Dict[str, Any]]) -> None:
    banner("POST-FLIGHT SUSTAINABILITY EVALUATION (DEBRIEF)")

    if not applied_decisions:
        print("  FINAL OUTPUT")
        print("    » Applied actions            : 0")
        print("    » Estimated fuel saving      : 0 kg")
        print("    » CO2 prevented              : 0 kg")
        print("  No sustainability steps were applied in this scenario.")
        print("  Standard procedures were followed for operational safety.")
        return

    total_fuel_saved_kg = 0.0
    print(
        f"  Flight ID: {ctx.flight_id.upper()}  |  Aircraft: {ctx.aircraft_type.upper()}  |  Current Phase: {ctx.phase.upper()}\n"
    )
    print("  Applied Green Actions:")

    for item in applied_decisions:
        if item["key"] == "step_climb":
            fuel_saved = ctx.step_climb_savings_kg
            total_fuel_saved_kg += fuel_saved
            print(f"    • [ALTITUDE OPTIMIZATION]: Climbed to higher flight level saving {fuel_saved:.0f} kg of fuel.")
        elif item["key"] == "idle_reverse":
            fuel_saved = 15.0
            total_fuel_saved_kg += fuel_saved
            print(f"    • [IDLE REVERSE]: Utilized {ctx.runway_length_m}m runway to save fuel and brake/engine wear. (~15 kg)")
        elif item["key"] == "single_engine_taxi":
            fuel_saved = ctx.taxi_time_min * 5.0
            total_fuel_saved_kg += fuel_saved
            print(
                f"    • [SINGLE ENGINE TAXI]: Shut down one engine during {ctx.taxi_time_min} min taxi, saving {fuel_saved:.0f} kg of fuel."
            )

    co2_saved_kg = total_fuel_saved_kg * 3.16

    print("\n  FINAL OUTPUT:")
    print(f"    » Total Estimated Fuel Saved : {total_fuel_saved_kg:.0f} kg")
    print(f"    » Prevented CO2 Emissions    : {co2_saved_kg:.1f} kg")
    print(f"    » Avg. Operational Confidence: {sum(d['confidence'] for d in applied_decisions) / len(applied_decisions):.0f}%")

    print("\n  Thank you for your valuable cockpit contributions to")
    print("  the airline's green operation goals and sustainability.")


def ask_pilot_feedback(ctx: FlightContext, decision: Dict[str, Any]) -> PilotChoice:
    print("\nPilot feedback:")
    print("  1 - Applied")
    print("  2 - Not Suitable")
    print("  3 - Ignored")
    print("  4 - Do not log")

    choice_map = {1: PilotChoice.APPLIED, 2: PilotChoice.NOT_SUITABLE, 3: PilotChoice.IGNORED, 4: PilotChoice.NO_LOG}

    while True:
        try:
            choice_num = int(input("Choice: ").strip())
            if choice_num not in choice_map:
                raise ValueError
            pilot_choice = choice_map[choice_num]
            break
        except ValueError:
            print("  ! Choose a number between 1-4.")

    if pilot_choice != PilotChoice.NO_LOG:
        note = input("Short note / reason: ").strip()
        impact = decision_impact_estimate(decision["key"], ctx)
        if pilot_choice == PilotChoice.APPLIED and decision["key"] == "step_climb":
            if note:
                note += f"; Estimated fuel saved: {ctx.step_climb_savings_kg:.0f} kg"
            else:
                note = f"Estimated fuel saved: {ctx.step_climb_savings_kg:.0f} kg"

        log_decision(ctx, decision, pilot_choice.value, note)
        print("  → Decision and context saved to CSV.")
        if pilot_choice == PilotChoice.APPLIED:
            print(
                f"  → Estimated output: fuel saving {impact['fuel_saved_kg']:.0f} kg | "
                f"CO2 prevented {impact['co2_prevented_kg']:.1f} kg"
            )

    return pilot_choice


def log_decision(ctx: FlightContext, decision: Dict[str, Any], pilot_choice: str, note: str = "") -> None:
    file_exists = LOG_FILE.exists()
    ctx_dict = asdict(ctx)

    headers = [
        "timestamp",
        "decision_name",
        "system_verdict",
        "confidence",
        "pilot_choice",
        "pilot_note",
    ]
    headers.extend(ctx_dict.keys())

    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    row = [
        timestamp,
        decision["name"],
        decision["verdict"],
        decision["confidence"],
        pilot_choice,
        note,
    ]
    row.extend(ctx_dict.values())

    with LOG_FILE.open("a", newline="", encoding="utf-8") as file_handle:
        writer = csv.writer(file_handle)
        if not file_exists:
            writer.writerow(headers)
        writer.writerow(row)


def review_loop(ctx: FlightContext) -> None:
    while True:
        clear_screen()
        print_context_review(ctx)
        action = ask_review_action()

        if action == "e" or action == "":
            decisions = evaluate_all(ctx)
            show_decision_screen(ctx, decisions)

            if ask_yes_no("\nDo you want to save this evaluation to CSV?", False):
                applied_decisions: List[Dict[str, Any]] = []
                for decision in decisions:
                    if decision["verdict_key"] == Verdict.SUPPRESSED.name:
                        continue
                    print("\n" + "-" * 80)
                    print(
                        Decision(
                            name=decision["name"],
                            verdict=Verdict[decision["verdict_key"]],
                            reasons=decision["reasons"],
                            caveats=decision["caveats"],
                            confidence=decision["confidence"],
                        ).render()
                    )
                    choice = ask_pilot_feedback(ctx, decision)
                    if choice == PilotChoice.APPLIED:
                        applied_decisions.append(decision)
                generate_sustainability_debrief(ctx, applied_decisions)

            input("\nPress Enter to continue...")
            return

        if action == "b":
            edit_from_question(len(QUESTIONS) - 1, ctx)
            continue

        if action == "j":
            print("\nQuestions:")
            for pos, question in enumerate(QUESTIONS, start=1):
                print(f"  {pos:02d}. {question.section} — {question.label}")
            while True:
                try:
                    choice = input("\nQuestion number to return to: ").strip()
                    index = int(choice)
                    if not (1 <= index <= len(QUESTIONS)):
                        raise ValueError
                    edit_from_question(index - 1, ctx)
                    break
                except ValueError:
                    print("  ! Enter a valid question number.")
            continue

        if action == "q":
            raise KeyboardInterrupt

        print("  ! Invalid choice.")
        input("  Press Enter to continue...")


def edit_from_question(start_index: int, ctx: FlightContext) -> None:
    answers = asdict(ctx)
    index = start_index
    total = len(QUESTIONS)

    while 0 <= index < total:
        question = QUESTIONS[index]
        current_value = answers.get(question.key, question.default)
        clear_screen()
        print(APP_NAME)
        question_prompt(question, index, total, current_value)

        try:
            raw = input("\nAnswer: ")
            parsed = parse_answer(question, raw, current_value)
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            return
        except ValueError as exc:
            print(f"\n  ! {exc}")
            input("  Press Enter to continue...")
            continue

        if parsed is BACK:
            if index == 0:
                print("\n  ! You are at the first question.")
                input("  Press Enter to continue...")
                continue
            index -= 1
            continue

        answers[question.key] = parsed
        index += 1

    updated = parse_context(answers)
    ctx.__dict__.update(asdict(updated))


def ask_yes_no(prompt: str, default: bool) -> bool:
    default_text = "Y/n" if default else "y/N"
    truthy = {"y", "yes", "true", "1", "on"}
    falsy = {"n", "no", "false", "0", "off"}

    while True:
        raw = input(f"{prompt} ({default_text}): ").strip().lower()
        if raw == "":
            return default
        if raw in truthy:
            return True
        if raw in falsy:
            return False
        print("  ! Y/N expected.")


GUI_PRESETS: Dict[str, FlightContext] = {
    "Cruise efficiency": FlightContext(
        flight_id="THY-CRZ-01",
        aircraft_type="A320",
        phase="cruise",
        crew_workload=2,
        abnormal_situation=False,
        sop_compatible=True,
        delay_pressure=False,
        icing_conditions=False,
        turbulence_forecast="none",
        low_visibility=False,
        crosswind_kt=0.0,
        tailwind_kt=0.0,
        runway_length_m=3000,
        braking_action="good",
        runway_contaminated=False,
        landing_weight_high=False,
        atc_constraints=False,
        traffic_density_high=False,
        taxi_time_min=12,
        step_climb_savings_kg=180.0,
    ),
    "Critical landing": FlightContext(
        flight_id="THY-LND-02",
        aircraft_type="A320",
        phase="landing",
        crew_workload=3,
        abnormal_situation=False,
        sop_compatible=True,
        delay_pressure=True,
        icing_conditions=False,
        turbulence_forecast="light",
        low_visibility=False,
        crosswind_kt=12.0,
        tailwind_kt=4.0,
        runway_length_m=2100,
        braking_action="medium",
        runway_contaminated=True,
        landing_weight_high=True,
        atc_constraints=False,
        traffic_density_high=True,
        taxi_time_min=8,
        step_climb_savings_kg=20.0,
    ),
    "Taxi efficiency": FlightContext(
        flight_id="THY-TAX-03",
        aircraft_type="A320",
        phase="taxi",
        crew_workload=2,
        abnormal_situation=False,
        sop_compatible=True,
        delay_pressure=False,
        icing_conditions=False,
        turbulence_forecast="none",
        low_visibility=False,
        crosswind_kt=6.0,
        tailwind_kt=0.0,
        runway_length_m=3000,
        braking_action="good",
        runway_contaminated=False,
        landing_weight_high=False,
        atc_constraints=False,
        traffic_density_high=False,
        taxi_time_min=18,
        step_climb_savings_kg=0.0,
    ),
}


def apply_modern_theme(app: QApplication) -> None:
    spin_up_icon = stylesheet_asset_path(SPIN_UP_ICON_PATH)
    spin_down_icon = stylesheet_asset_path(SPIN_DOWN_ICON_PATH)
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#F4F5F6"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor("#f6f6f6"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#232B38"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#ffffff"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#232B38"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#E3000F"))  # THY Red
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)
    app.setFont(QFont("Segoe UI", 10))
    app.setStyleSheet(
        """
        QMainWindow { background: #F4F5F6; }
        QWidget { color: #232B38; font-family: "Segoe UI"; }
        QFrame#wizardCard, QFrame#resultCard, QFrame#headerCard, QFrame#summaryCard {
            background: #ffffff;
            border: 1px solid #d9d9d9;
            border-radius: 16px;
        }
        QFrame#resultHero {
            background: #ffffff;
            border: 1px solid #d9d9d9;
            border-radius: 18px;
        }
        QLabel#brandTitle {
            color: #E3000F; /* THY Red */
            font-size: 24px;
            font-weight: 700;
        }
        QLabel#brandSubtitle, QLabel#mutedText {
            color: #666666;
        }
        QLabel#sectionLabel {
            color: #8a8a8a;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
        }
        QLabel#questionTitle {
            color: #232B38;
            font-size: 22px;
            font-weight: 700;
        }
        QLabel#questionHint {
            color: #4f4f4f;
            font-size: 11px;
        }
        QPushButton#stepChip {
            color: #666666;
            font-size: 12px;
            font-weight: 600;
            padding: 8px 12px;
            border-radius: 999px;
            background: #f2f2f2;
            border: 1px solid #e2e2e2;
            min-height: 18px;
        }
        QPushButton#stepChip:hover[state="pending"],
        QPushButton#stepChip:hover[state="completed"] {
            background: #ececec;
            border: 1px solid #d8d8d8;
        }
        QPushButton#stepChip[state="completed"] {
            color: #7a0014;
            background: #eadfe2;
            border: 1px solid #d8b7bf;
        }
        QPushButton#stepChip[state="active"] {
            color: #6b0012;
            background: #f4d9de;
            border: 1px solid #c8102e;
        }
        QPushButton#stepChip[state="active"]:hover {
            color: #6b0012;
            background: #f4d9de;
            border: 1px solid #c8102e;
        }
        QPushButton#stepChip[state="pending"] {
            color: #666666;
            background: #f2f2f2;
            border: 1px solid #e2e2e2;
        }
        QLabel#statusBadge {
            padding: 6px 12px;
            border-radius: 999px;
            font-weight: 700;
        }
        QLabel#statusBadge[verdict="RECOMMEND"] { background: #fde8ea; color: #9b1027; border: 1px solid #f2b3bc; }
        QLabel#statusBadge[verdict="CONDITIONAL"] { background: #f7f7f7; color: #444444; border: 1px solid #d8d8d8; }
        QLabel#statusBadge[verdict="DO_NOT_RECOMMEND"] { background: #fde8ea; color: #9b1027; border: 1px solid #f2b3bc; }
        QLabel#statusBadge[verdict="SUPPRESSED"] { background: #f0f0f0; color: #777777; border: 1px solid #dddddd; }
        QLabel#decisionIcon, QLabel#heroIcon, QLabel#metricIcon, QLabel#outputIcon {
            border-radius: 14px;
            font-size: 18px;
            font-weight: 700;
            min-width: 28px;
            min-height: 28px;
            padding: 6px;
            text-align: center;
        }
        QLabel#decisionIcon {
            background: #fde8ea;
            color: #9b1027;
        }
        QLabel#heroIcon {
            background: #eaf7ef;
            color: #1f7a3d;
        }
        QLabel#metricIcon {
            background: #f3f3f3;
            color: #232B38;
        }
        QLabel#outputIcon {
            background: #eaf7ef;
            color: #1f7a3d;
        }
        QLabel#heroState {
            font-size: 21px;
            font-weight: 700;
            color: #232B38;
        }
        QLabel#heroSummary {
            color: #4f4f4f;
        }
        QLabel#metricLabel {
            color: #666666;
            font-size: 9px;
            text-transform: uppercase;
            font-weight: 700;
        }
        QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
            background: #ffffff;
            border: 1px solid #d9d9d9;
            border-radius: 10px;
            padding: 8px 34px 8px 10px;
            min-height: 28px;
        }
        QSpinBox::up-button, QDoubleSpinBox::up-button,
        QSpinBox::down-button, QDoubleSpinBox::down-button {
            width: 24px;
            background: #f3e3e7;
            border-left: 1px solid #cfaab3;
        }
        QSpinBox::up-button, QDoubleSpinBox::up-button {
            border-top-right-radius: 10px;
            border-bottom: 1px solid #cfaab3;
        }
        QSpinBox::down-button, QDoubleSpinBox::down-button {
            border-bottom-right-radius: 10px;
        }
        QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
        QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {
            background: #e8cfd6;
        }
        QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
            image: url("%(spin_up_icon)s");
            width: 10px;
            height: 10px;
        }
        QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
            image: url("%(spin_down_icon)s");
            width: 10px;
            height: 10px;
        }
        QComboBox::drop-down { border: 0px; width: 28px; }
        QComboBox QAbstractItemView {
            background: #ffffff;
            border: 1px solid #d9d9d9;
            selection-background-color: #fde8ea;
            selection-color: #232B38;
        }
        QPushButton {
            background: #f6f6f6;
            border: 1px solid #d9d9d9;
            border-radius: 10px;
            padding: 10px 14px;
            font-weight: 600;
        }
        QPushButton:hover { background: #eeeeee; }
        QPushButton#primaryButton {
            background: #E3000F;
            border: 1px solid #E3000F;
            color: white;
        }
        QPushButton#primaryButton:hover { background: #B3000C; }
        QPushButton:disabled { color: #999999; background: #f2f2f2; }
        QProgressBar {
            border: 1px solid #d9d9d9;
            border-radius: 8px;
            background: #ffffff;
            text-align: center;
            height: 18px;
        }
        QProgressBar::chunk {
            border-radius: 8px;
            background: #E3000F;
        }
        QScrollBar:horizontal {
            height: 10px;
            background: transparent;
            margin: 4px 0 0 0;
        }
        QScrollBar::handle:horizontal {
            background: #d0d0d0;
            border-radius: 5px;
            min-width: 60px;
        }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        QScrollArea { border: none; background: transparent; }
        """
        % {
            "spin_up_icon": spin_up_icon,
            "spin_down_icon": spin_down_icon,
        }
    )


QUESTION_UI = {
    "flight_id": ("Flight / scenario ID", "Enter a unique flight or scenario identifier."),
    "aircraft_type": ("Aircraft type", "Example: A320, B737, A350."),
    "phase": ("Flight phase", "Choose the current operational phase."),
    "crew_workload": ("Crew workload", "1 = low, 5 = high."),
    "abnormal_situation": ("Abnormal situation active?", "Use this to silence the system."),
    "sop_compatible": ("SOP compliant?", "Disable if the action conflicts with SOP."),
    "delay_pressure": ("Delay / time pressure?", "Operational pressure note."),
    "icing_conditions": ("Icing conditions present?", "Weather input."),
    "turbulence_forecast": ("Turbulence forecast", "Forecast for the current sector."),
    "low_visibility": ("Low visibility?", "Critical in taxi, takeoff, approach, and landing."),
    "crosswind_kt": ("Crosswind (kt)", "Numeric value in knots."),
    "tailwind_kt": ("Tailwind (kt)", "Numeric value in knots."),
    "runway_length_m": ("Runway length (m)", "Available runway length."),
    "braking_action": ("Braking action", "Runway surface condition."),
    "runway_contaminated": ("Runway contaminated?", "Wet / slush / snow / ice conditions."),
    "landing_weight_high": ("High landing weight?", "Landing weight is above normal."),
    "atc_constraints": ("ATC constraints?", "ATC clearance or constraints exist."),
    "traffic_density_high": ("High traffic density?", "Traffic complexity is elevated."),
    "taxi_time_min": ("Expected taxi time (min)", "Estimated taxi duration."),
    "step_climb_savings_kg": ("Estimated step climb fuel savings (kg)", "Fuel savings estimate."),
}


class WizardStepBar(QScrollArea):
    def __init__(self, questions: List[Question], on_step_clicked) -> None:
        super().__init__()
        self.questions = questions
        self.on_step_clicked = on_step_clicked

        self.setWidgetResizable(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setFixedHeight(74)
        self.setStyleSheet("background: transparent;")

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        layout = QHBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.labels: List[QPushButton] = []
        for index, question in enumerate(questions, start=1):
            label = QPushButton(f"{index}. {QUESTION_UI[question.key][0]}")
            label.setObjectName("stepChip")
            label.setProperty("state", "pending")
            label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
            label.setCursor(Qt.CursorShape.PointingHandCursor)
            label.setFlat(True)
            label.clicked.connect(lambda _checked=False, step=index - 1: self.on_step_clicked(step))
            self.labels.append(label)
            layout.addWidget(label)

        layout.addStretch(1)
        self.setWidget(content)

    def set_active(self, index: int) -> None:
        for position, label in enumerate(self.labels):
            if position < index:
                label.setProperty("state", "completed")
            elif position == index:
                label.setProperty("state", "active")
                self.ensureWidgetVisible(label, 50, 0)
            else:
                label.setProperty("state", "pending")

            label.style().unpolish(label)
            label.style().polish(label)


class QuestionPage(QFrame):
    def __init__(self, question: Question) -> None:
        super().__init__()
        self.question = question
        self.value_control: Optional[QWidget] = None
        self.setObjectName("wizardCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 24, 32, 24)
        layout.setSpacing(0)
        layout.addStretch(1)

        content = QWidget()
        content.setMaximumWidth(500)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(16)

        section = QLabel(question.section)
        section.setObjectName("sectionLabel")
        section.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(section)

        title = QLabel(QUESTION_UI[question.key][0])
        title.setObjectName("questionTitle")
        title.setWordWrap(True)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setMinimumHeight(82)
        content_layout.addWidget(title)

        hint = QLabel(QUESTION_UI[question.key][1])
        hint.setObjectName("questionHint")
        hint.setWordWrap(True)
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(hint)

        self.control = self._build_control()
        self.control.setMinimumHeight(44)
        self.control.setMinimumWidth(320)
        self.control.setMaximumWidth(360)
        content_layout.addWidget(self.control, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(content, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(1)

    def _build_control(self) -> QWidget:
        if self.question.kind == "bool":
            wrapper = QWidget()
            wrapper_layout = QHBoxLayout(wrapper)
            wrapper_layout.setContentsMargins(0, 0, 0, 0)
            wrapper_layout.setSpacing(0)
            wrapper_layout.addStretch(1)
            widget = QCheckBox("Enabled")
            widget.setChecked(bool(self.question.default))
            wrapper_layout.addWidget(widget, 0, Qt.AlignmentFlag.AlignCenter)
            wrapper_layout.addStretch(1)
            self.value_control = widget
            return wrapper
        if self.question.kind == "choice":
            widget = QComboBox()
            widget.addItems(self.question.choices)
            if self.question.default in self.question.choices:
                widget.setCurrentText(self.question.default)
            self.value_control = widget
            return widget
        if self.question.kind == "int":
            widget = QSpinBox()
            widget.setRange(
                int(self.question.minimum if self.question.minimum is not None else -10_000),
                int(self.question.maximum if self.question.maximum is not None else 10_000),
            )
            widget.setValue(int(self.question.default))
            self.value_control = widget
            return widget
        if self.question.kind == "float":
            widget = QDoubleSpinBox()
            widget.setDecimals(1)
            widget.setRange(
                float(self.question.minimum if self.question.minimum is not None else -10_000.0),
                float(self.question.maximum if self.question.maximum is not None else 10_000.0),
            )
            widget.setValue(float(self.question.default))
            self.value_control = widget
            return widget
        widget = QLineEdit()
        widget.setText(str(self.question.default))
        self.value_control = widget
        return widget

    def get_value(self) -> Any:
        widget = self.value_control
        if isinstance(widget, QCheckBox):
            return widget.isChecked()
        if isinstance(widget, QComboBox):
            return widget.currentText()
        if isinstance(widget, QSpinBox):
            return int(widget.value())
        if isinstance(widget, QDoubleSpinBox):
            return float(widget.value())
        if isinstance(widget, QLineEdit):
            return widget.text().strip()
        return self.question.default

    def set_value(self, value: Any) -> None:
        widget = self.value_control
        if isinstance(widget, QCheckBox):
            widget.setChecked(bool(value))
        elif isinstance(widget, QComboBox):
            index = widget.findText(str(value))
            if index >= 0:
                widget.setCurrentIndex(index)
        elif isinstance(widget, QSpinBox):
            widget.setValue(int(value))
        elif isinstance(widget, QDoubleSpinBox):
            widget.setValue(float(value))
        elif isinstance(widget, QLineEdit):
            widget.setText(str(value))

    def focus_control(self) -> None:
        target = self.value_control if self.value_control is not None else self.control
        target.setFocus()


class ResultCard(QFrame):
    def __init__(self, decision: Dict[str, Any], save_callback, context: FlightContext) -> None:
        super().__init__()
        self.decision = decision
        self.save_callback = save_callback
        self.context = context
        self.setObjectName("resultCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        visual = verdict_visual(decision["verdict_key"])

        top_row = QHBoxLayout()
        top_row.setSpacing(12)

        icon = QLabel(visual["icon"])
        icon.setObjectName("decisionIcon")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet(f"background:{visual['bg']}; color:{visual['accent']}; border: 1px solid {visual['border']};")
        top_row.addWidget(icon, 0, Qt.AlignmentFlag.AlignTop)

        left = QVBoxLayout()
        left.setSpacing(4)

        title = QLabel(decision["name"])
        title.setObjectName("questionTitle")
        left.addWidget(title)

        subtitle = QLabel(f"Decision key: {decision['key']}")
        subtitle.setObjectName("questionHint")
        left.addWidget(subtitle)

        top_row.addLayout(left, 1)

        badge = QLabel(decision["verdict"])
        badge.setObjectName("statusBadge")
        badge.setProperty("verdict", decision["verdict_key"])
        badge.setStyleSheet(
            f"background:{visual['bg']}; color:{visual['accent']}; border:1px solid {visual['border']};"
        )
        badge.style().unpolish(badge)
        badge.style().polish(badge)
        top_row.addWidget(badge, 0, Qt.AlignmentFlag.AlignTop)
        layout.addLayout(top_row)

        def add_metric(row: QHBoxLayout, icon_text: str, label_text: str, value_text: str) -> None:
            box = QFrame()
            box.setObjectName("metricCard")
            box_layout = QVBoxLayout(box)
            box_layout.setContentsMargins(12, 10, 12, 10)
            box_layout.setSpacing(4)
            header = QHBoxLayout()
            metric_icon_label = QLabel(icon_text)
            metric_icon_label.setObjectName("metricIcon")
            metric_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header.addWidget(metric_icon_label, 0, Qt.AlignmentFlag.AlignLeft)
            label = QLabel(label_text)
            label.setObjectName("metricLabel")
            header.addWidget(label, 1)
            header.addStretch(1)
            box_layout.addLayout(header)
            value = QLabel(value_text)
            value.setStyleSheet("font-size: 16px; font-weight: 700;")
            box_layout.addWidget(value)
            box.setStyleSheet("background:#f8f8f8;border:1px solid #e1e1e1;border-radius:12px;")
            row.addWidget(box, 1)

        metric_row = QHBoxLayout()
        add_metric(metric_row, metric_icon("confidence"), "Confidence", f"{decision['confidence']}%")
        add_metric(metric_row, metric_icon("fuel"), "Fuel saving", f"{decision['fuel_saved_kg_estimate']:.0f} kg")
        add_metric(metric_row, metric_icon("co2"), "CO2 prevented", f"{decision['co2_prevented_kg_estimate']:.1f} kg")
        layout.addLayout(metric_row)

        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(int(decision["confidence"]))
        layout.addWidget(bar)

        reasons = QLabel(
            "Reasons:\n"
            + (
                "\n".join(f"• {item}" for item in decision["reasons"])
                if decision["reasons"]
                else "• None"
            )
        )
        reasons.setWordWrap(True)
        layout.addWidget(reasons)

        caveats = QLabel(
            "Notes / constraints:\n"
            + (
                "\n".join(f"• {item}" for item in decision["caveats"])
                if decision["caveats"]
                else "• None"
            )
        )
        caveats.setWordWrap(True)
        layout.addWidget(caveats)

        row = QHBoxLayout()
        self.choice_box = QComboBox()
        for choice in PilotChoice:
            self.choice_box.addItem(choice.value, choice.name)
        self.choice_box.setCurrentIndex(self.choice_box.findData(PilotChoice.NO_LOG.name))
        self.note_edit = QLineEdit()
        self.note_edit.setPlaceholderText("Optional pilot note")
        self.save_button = QPushButton("Save log")
        self.save_button.setObjectName("primaryButton")
        self.save_button.clicked.connect(self._save)
        row.addWidget(self.choice_box, 0)
        row.addWidget(self.note_edit, 1)
        row.addWidget(self.save_button, 0)
        layout.addLayout(row)

        self.status = QLabel("No log yet.")
        self.status.setObjectName("mutedText")
        layout.addWidget(self.status)

    def _save(self) -> None:
        choice_name = self.choice_box.currentData()
        note = self.note_edit.text().strip()
        self.status.setText(self.save_callback(self.decision["key"], choice_name, note))


class ResultPage(QFrame):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("wizardCard")
        self.cards: List[ResultCard] = []
        self.save_callback = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(14)

        self.hero_card = QFrame()
        self.hero_card.setObjectName("resultHero")
        hero_layout = QHBoxLayout(self.hero_card)
        hero_layout.setContentsMargins(18, 18, 18, 18)
        hero_layout.setSpacing(14)

        self.hero_icon = QLabel("✓")
        self.hero_icon.setObjectName("heroIcon")
        self.hero_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hero_layout.addWidget(self.hero_icon, 0, Qt.AlignmentFlag.AlignTop)

        hero_text = QVBoxLayout()
        hero_text.setSpacing(4)
        self.hero_title = QLabel("Evaluation result")
        self.hero_title.setObjectName("heroState")
        hero_text.addWidget(self.hero_title)

        self.summary_label = QLabel()
        self.summary_label.setObjectName("heroSummary")
        self.summary_label.setWordWrap(True)
        hero_text.addWidget(self.summary_label)
        hero_layout.addLayout(hero_text, 1)

        self.hero_pill = QLabel("Ready")
        self.hero_pill.setObjectName("statusBadge")
        self.hero_pill.setProperty("verdict", Verdict.CONDITIONAL.name)
        self.hero_pill.setStyleSheet("background:#f7f7f7;color:#444444;border:1px solid #d8d8d8;")
        self.hero_pill.style().unpolish(self.hero_pill)
        self.hero_pill.style().polish(self.hero_pill)
        hero_layout.addWidget(self.hero_pill, 0, Qt.AlignmentFlag.AlignTop)

        layout.addWidget(self.hero_card)

        self.debrief_card = QFrame()
        self.debrief_card.setObjectName("summaryCard")
        self.debrief_layout = QVBoxLayout(self.debrief_card)
        self.debrief_layout.setContentsMargins(16, 16, 16, 16)
        self.debrief_layout.setSpacing(6)
        layout.addWidget(self.debrief_card)

        self.final_output_card = QFrame()
        self.final_output_card.setObjectName("summaryCard")
        self.final_output_layout = QVBoxLayout(self.final_output_card)
        self.final_output_layout.setContentsMargins(16, 16, 16, 16)
        self.final_output_layout.setSpacing(10)

        final_title_row = QHBoxLayout()
        self.final_output_icon = QLabel(metric_icon("summary"))
        self.final_output_icon.setObjectName("outputIcon")
        self.final_output_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.final_output_icon.setStyleSheet("background:#eaf7ef; color:#1f7a3d; border:1px solid #b8e0c4;")
        final_title_row.addWidget(self.final_output_icon, 0, Qt.AlignmentFlag.AlignTop)

        final_title_text = QVBoxLayout()
        self.final_output_title = QLabel("Final output")
        self.final_output_title.setStyleSheet("font-size: 18px; font-weight: 700;")
        final_title_text.addWidget(self.final_output_title)

        self.final_output_summary = QLabel("No applied actions logged yet.")
        self.final_output_summary.setWordWrap(True)
        self.final_output_summary.setStyleSheet("color: #4f4f4f;")
        final_title_text.addWidget(self.final_output_summary)
        final_title_row.addLayout(final_title_text, 1)
        self.final_output_layout.addLayout(final_title_row)

        metric_row = QHBoxLayout()
        self.applied_count_label = self._create_metric_box(metric_row, metric_icon("applied"), "Applied actions", "0")
        self.applied_fuel_label = self._create_metric_box(metric_row, metric_icon("fuel"), "Estimated fuel saving", "0 kg")
        self.applied_co2_label = self._create_metric_box(metric_row, metric_icon("co2"), "CO2 prevented", "0 kg")
        self.final_output_layout.addLayout(metric_row)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(12)
        self.scroll.setWidget(self.scroll_content)
        layout.addWidget(self.scroll, 1)

    def set_save_callback(self, callback) -> None:
        self.save_callback = callback

    def _create_metric_box(self, row: QHBoxLayout, icon_text: str, label_text: str, value_text: str) -> QLabel:
        box = QFrame()
        box.setObjectName("metricCard")
        box_layout = QVBoxLayout(box)
        box_layout.setContentsMargins(12, 10, 12, 10)
        box_layout.setSpacing(4)
        header = QHBoxLayout()
        icon = QLabel(icon_text)
        icon.setObjectName("metricIcon")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.addWidget(icon, 0, Qt.AlignmentFlag.AlignLeft)
        label = QLabel(label_text)
        label.setObjectName("metricLabel")
        header.addWidget(label, 1)
        header.addStretch(1)
        box_layout.addLayout(header)
        value = QLabel(value_text)
        value.setStyleSheet("font-size: 16px; font-weight: 700;")
        box_layout.addWidget(value)
        box.setStyleSheet("background:#f8f8f8;border:1px solid #e1e1e1;border-radius:12px;")
        row.addWidget(box, 1)
        return value

    def update_applied_output(self, applied_estimates: Dict[str, Dict[str, float]]) -> None:
        applied_count = len(applied_estimates)
        total_fuel = sum(item["fuel_saved_kg"] for item in applied_estimates.values())
        total_co2 = sum(item["co2_prevented_kg"] for item in applied_estimates.values())

        if applied_count:
            summary_text = "This output reflects decisions that were logged as Applied in the current session."
        else:
            summary_text = "No applied actions logged yet. Save a decision as Applied to populate this output."

        self.final_output_summary.setText(summary_text)
        self.applied_count_label.setText(str(applied_count))
        self.applied_fuel_label.setText(f"{total_fuel:.0f} kg")
        self.applied_co2_label.setText(f"{total_co2:.1f} kg")
        if applied_count:
            self.hero_icon.setText("✓")
            self.hero_icon.setStyleSheet("background:#eaf7ef; color:#1f7a3d; border:1px solid #b8e0c4;")
            self.hero_pill.setText("Applied actions present")
            self.hero_pill.setProperty("verdict", Verdict.RECOMMEND.name)
            self.hero_pill.setStyleSheet("background:#eaf7ef;color:#1f7a3d;border:1px solid #b8e0c4;")
        else:
            self.hero_icon.setText("◌")
            self.hero_icon.setStyleSheet("background:#f0f0f0; color:#666666; border:1px solid #dddddd;")
            self.hero_pill.setText("Waiting for applied log")
            self.hero_pill.setProperty("verdict", Verdict.SUPPRESSED.name)
            self.hero_pill.setStyleSheet("background:#f0f0f0;color:#777777;border:1px solid #dddddd;")
        self.hero_pill.style().unpolish(self.hero_pill)
        self.hero_pill.style().polish(self.hero_pill)

    def populate(
        self,
        context: FlightContext,
        decisions: List[Dict[str, Any]],
        summary: Dict[str, Any],
        applied_estimates: Optional[Dict[str, Dict[str, float]]] = None,
    ) -> None:
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        while self.debrief_layout.count():
            item = self.debrief_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        if summary["overall_state"] == "SYSTEM SILENCED":
            visual_key = "SUPPRESSED"
        elif summary["not_recommend"] > summary["recommended"] and summary["not_recommend"] >= summary["conditional"]:
            visual_key = "DO_NOT_RECOMMEND"
        elif summary["recommended"] >= summary["not_recommend"]:
            visual_key = "RECOMMEND"
        else:
            visual_key = "CONDITIONAL"
        overall_visual = verdict_visual(visual_key)
        self.hero_icon.setText(overall_visual["icon"])
        self.hero_icon.setStyleSheet(
            f"background:{overall_visual['bg']}; color:{overall_visual['accent']}; border:1px solid {overall_visual['border']};"
        )
        self.hero_title.setText(f"{summary['overall_state'].title()} overview")
        self.summary_label.setText(
            f"Flight ID: {context.flight_id} | Aircraft: {context.aircraft_type} | Phase: {context.phase}\n"
            f"Average confidence: {summary['average_confidence']}% | Fuel savings: {summary['estimated_fuel_kg']} kg | "
            f"CO2 prevented: {summary['estimated_co2_kg']} kg"
        )
        self.hero_pill.setText(
            f"{metric_icon('applied')} {summary['recommended']} recommended | "
            f"{metric_icon('fuel')} {summary['estimated_fuel_kg']} kg fuel | "
            f"{metric_icon('co2')} {summary['estimated_co2_kg']} kg CO2"
        )
        self.hero_pill.setProperty("verdict", Verdict.CONDITIONAL.name)
        self.hero_pill.setStyleSheet(
            "background:#f7f7f7;color:#444444;border:1px solid #d8d8d8;"
        )
        self.hero_pill.style().unpolish(self.hero_pill)
        self.hero_pill.style().polish(self.hero_pill)

        for line in [
            f"Overall state: {summary['overall_state']}",
            f"Recommended: {summary['recommended']} | Conditional: {summary['conditional']} | Not recommended: {summary['not_recommend']} | Silent: {summary['suppressed']}",
            "Final responsibility always remains with the flight crew.",
        ]:
            label = QLabel(line)
            label.setWordWrap(True)
            self.debrief_layout.addWidget(label)

        self.cards = []
        for decision in decisions:
            card = ResultCard(decision, self.save_callback, context)
            self.cards.append(card)
            self.scroll_layout.addWidget(card)
        self.update_applied_output(applied_estimates or {})
        self.scroll_layout.addWidget(self.final_output_card)
        self.scroll_layout.addStretch(1)


class AviationMainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Aero DSS | Assistant Wizard")
        icon_path = app_icon_path()
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))
        self.current_step = 0
        self.current_evaluation: Optional[Dict[str, Any]] = None
        self.applied_estimates: Dict[str, Dict[str, float]] = {}

        self.pages: List[QuestionPage] = [QuestionPage(question) for question in QUESTIONS]
        self.result_page = ResultPage()
        self.result_page.set_save_callback(self._save_decision)

        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(18, 18, 18, 18)
        root_layout.setSpacing(14)

        root_layout.addWidget(self._build_header())
        self.step_bar = WizardStepBar(QUESTIONS, self.go_to_step)
        root_layout.addWidget(self.step_bar)

        self.stack = QStackedWidget()
        for page in self.pages:
            self.stack.addWidget(page)
        self.stack.addWidget(self.result_page)
        root_layout.addWidget(self.stack, 1)

        root_layout.addWidget(self._build_footer())
        self.setCentralWidget(root)

        self._install_shortcuts()
        self._apply_defaults()
        self._sync_ui()

    def _build_header(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("headerCard")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(18, 16, 18, 16)

        title_col = QVBoxLayout()
        title = QLabel("Aero DSS")
        title.setObjectName("brandTitle")
        subtitle = QLabel("A simple assistant-style wizard for aviation decisions.")
        subtitle.setObjectName("brandSubtitle")
        title_col.addWidget(title)
        title_col.addWidget(subtitle)

        self.preset_box = QComboBox()
        self.preset_box.addItem("Load preset", "")
        for name in GUI_PRESETS:
            self.preset_box.addItem(name, name)
        self.preset_box.currentIndexChanged.connect(self._preset_selected)
        self.preset_box.setMinimumWidth(220)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, len(QUESTIONS))
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%v / %m")
        self.progress_bar.setMinimumWidth(220)

        layout.addLayout(title_col, 1)
        layout.addWidget(self.preset_box, 0)
        layout.addWidget(self.progress_bar, 0)
        return frame

    def _build_footer(self) -> QFrame:
        frame = QFrame()
        frame.setObjectName("headerCard")
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(18, 14, 18, 14)

        self.step_label = QLabel("Step 1 of {}".format(len(QUESTIONS)))
        self.step_label.setObjectName("mutedText")
        layout.addWidget(self.step_label)
        layout.addStretch(1)

        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(self.go_back)
        self.next_button = QPushButton("Next")
        self.next_button.setObjectName("primaryButton")
        self.next_button.clicked.connect(self.go_next)
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self._apply_defaults)
        self.fullscreen_button = QPushButton("Fullscreen")
        self.fullscreen_button.clicked.connect(self.toggle_fullscreen)

        layout.addWidget(self.back_button)
        layout.addWidget(self.next_button)
        layout.addWidget(self.reset_button)
        layout.addWidget(self.fullscreen_button)
        return frame

    def toggle_fullscreen(self) -> None:
        if self.isFullScreen():
            self.showNormal()
            self.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        else:
            self.showFullScreen()

    def _install_shortcuts(self) -> None:
        QShortcut(QKeySequence("Alt+Left"), self, self.go_back)
        QShortcut(QKeySequence("Alt+Right"), self, self.go_next)
        QShortcut(QKeySequence("Ctrl+Return"), self, self.go_next)
        QShortcut(QKeySequence("Ctrl+Enter"), self, self.go_next)
        QShortcut(QKeySequence("F11"), self, self.toggle_fullscreen)
        QShortcut(QKeySequence("Esc"), self, self._exit_fullscreen)

    def _exit_fullscreen(self) -> None:
        if self.isFullScreen():
            self.showNormal()
            self.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)

    def _apply_defaults(self) -> None:
        self.load_context(FlightContext())
        self.current_step = 0
        self.current_evaluation = None
        self.applied_estimates = {}
        self.result_page.update_applied_output(self.applied_estimates)
        self.stack.setCurrentIndex(0)
        self._sync_ui()

    def load_context(self, context: FlightContext) -> None:
        values = asdict(context)
        for page in self.pages:
            page.set_value(values[page.question.key])

    def current_context(self) -> FlightContext:
        payload = {page.question.key: page.get_value() for page in self.pages}
        return parse_context(payload)

    def _preset_selected(self) -> None:
        key = self.preset_box.currentData()
        if not key:
            return
        preset = GUI_PRESETS.get(key)
        if preset is None:
            return
        self.load_context(preset)
        self.current_step = 0
        self.current_evaluation = None
        self.applied_estimates = {}
        self.result_page.update_applied_output(self.applied_estimates)
        self.stack.setCurrentIndex(0)
        self._sync_ui()

    def _sync_ui(self) -> None:
        active_index = min(self.current_step, len(QUESTIONS) - 1)
        self.step_bar.set_active(active_index)
        self.progress_bar.setValue(min(self.current_step, len(QUESTIONS)))
        if self.current_step >= len(QUESTIONS):
            self.step_label.setText("Review results")
        else:
            self.step_label.setText(f"Step {self.current_step + 1} of {len(QUESTIONS)}")
        self.back_button.setEnabled(self.current_step > 0)
        if self.current_step == len(QUESTIONS):
            self.next_button.setText("Re-evaluate")
        elif self.current_step == len(QUESTIONS) - 1:
            self.next_button.setText("Evaluate")
        else:
            self.next_button.setText("Next")

        if self.current_step < len(self.pages):
            self.pages[self.current_step].focus_control()

    def go_back(self) -> None:
        if self.current_step <= 0:
            return
        self.current_step -= 1
        self.stack.setCurrentIndex(self.current_step)
        self._sync_ui()

    def go_next(self) -> None:
        if self.current_step < len(QUESTIONS) - 1:
            self.current_step += 1
            self.stack.setCurrentIndex(self.current_step)
            self._sync_ui()
            return
        if self.current_step == len(QUESTIONS) - 1:
            self._evaluate()
            self.current_step = len(QUESTIONS)
            self.stack.setCurrentIndex(len(QUESTIONS))
            self._sync_ui()
            return
        self._evaluate()
        self.stack.setCurrentIndex(len(QUESTIONS))
        self._sync_ui()

    def go_to_step(self, step_index: int) -> None:
        if step_index < 0 or step_index > len(QUESTIONS):
            return
        if step_index == len(QUESTIONS):
            if self.current_evaluation is None:
                self._evaluate()
            self.current_step = len(QUESTIONS)
            self.stack.setCurrentIndex(len(QUESTIONS))
            self._sync_ui()
            return
        self.current_step = step_index
        self.stack.setCurrentIndex(step_index)
        self._sync_ui()

    def _evaluate(self) -> None:
        context = self.current_context()
        decisions = evaluate_all(context)
        summary = scenario_summary(decisions, context)
        self.current_evaluation = {"context": context, "decisions": decisions}
        self.result_page.populate(context, decisions, summary, self.applied_estimates)

    def _save_decision(self, decision_key: str, choice_name: str, note: str) -> str:
        if self.current_evaluation is None:
            return "Evaluate the scenario first."
        context: FlightContext = self.current_evaluation["context"]
        choice_enum = PilotChoice[choice_name]
        if choice_enum == PilotChoice.NO_LOG:
            return "Log skipped."

        decision_payload = next((d for d in self.current_evaluation["decisions"] if d["key"] == decision_key), None)
        if not decision_payload:
            return "Error saving log."

        log_decision(context, decision_payload, choice_enum.value, note)
        if choice_enum == PilotChoice.APPLIED:
            self.applied_estimates[decision_key] = decision_impact_estimate(decision_key, context)
            self.result_page.update_applied_output(self.applied_estimates)
            impact = self.applied_estimates[decision_key]
            return (
                "Saved to CSV. "
                f"Estimated fuel saving: {impact['fuel_saved_kg']:.0f} kg | "
                f"CO2 prevented: {impact['co2_prevented_kg']:.1f} kg."
            )

        self.applied_estimates.pop(decision_key, None)
        self.result_page.update_applied_output(self.applied_estimates)
        return "Saved to CSV."


def run_gui() -> None:
    if PYQT_AVAILABLE and QT_BINDING in {"PyQt6", "PySide6"}:
        app = QApplication(sys.argv)
        apply_modern_theme(app)
        icon_path = app_icon_path()
        if icon_path:
            app.setWindowIcon(QIcon(icon_path))
        window = AviationMainWindow()
        window.resize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
        window.show()
        sys.exit(app.exec())

    run_tkinter_gui()


def run_tkinter_gui() -> None:
    import tkinter as tk
    from tkinter import messagebox, ttk

    class ScrollableFrame(ttk.Frame):
        def __init__(self, parent: tk.Widget, height: int = 220) -> None:
            super().__init__(parent)
            self.canvas = tk.Canvas(self, highlightthickness=0, bg="#f4f5f6", height=height)
            self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
            self.content = ttk.Frame(self.canvas)
            self.content.bind(
                "<Configure>",
                lambda _event: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
            )
            self.canvas_window = self.canvas.create_window((0, 0), window=self.content, anchor="nw")
            self.canvas.configure(yscrollcommand=self.scrollbar.set)
            self.canvas.pack(side="left", fill="both", expand=True)
            self.scrollbar.pack(side="right", fill="y")
            self.canvas.bind(
                "<Configure>",
                lambda event: self.canvas.itemconfigure(self.canvas_window, width=event.width),
            )

    class WizardApp:
        def __init__(self) -> None:
            self.root = tk.Tk()
            self.root.title("Aero DSS | Assistant Wizard")
            self.root.configure(bg="#f4f5f6")
            self.root.geometry(f"{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}")
            self.root.minsize(DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT)
            self.icon_image: Any = None
            icon_path = app_icon_path()
            if icon_path:
                try:
                    self.icon_image = tk.PhotoImage(file=icon_path)
                    self.root.iconphoto(True, self.icon_image)
                except tk.TclError:
                    self.icon_image = None

            self.values = asdict(FlightContext())
            self.current_index = 0
            self.current_var: Any = None
            self.current_decisions: List[Dict[str, Any]] = []
            self.current_summary: Dict[str, Any] = {}
            self.applied_estimates: Dict[str, Dict[str, float]] = {}
            self.result_cards: List[tk.Frame] = []
            self.step_buttons: List[tk.Button] = []
            self.preset_var = tk.StringVar(value="Load preset")
            self.status_var = tk.StringVar(value="Step 1 of {}".format(len(QUESTIONS)))
            self.progress_var = tk.IntVar(value=0)
            self.fullscreen_state = False
            self.applied_output_card: Any = None

            self._build_style()
            self._build_header()
            self._build_step_rail()
            self._build_main_area()
            self._build_footer()
            self._bind_shortcuts()
            self.root.bind("<Configure>", self._handle_window_resize)
            self._set_fullscreen(False)
            self._apply_values(FlightContext())
            self._show_question(0)

        def _build_style(self) -> None:
            style = ttk.Style(self.root)
            try:
                style.theme_use("clam")
            except tk.TclError:
                pass
            style.configure("App.TFrame", background="#f4f5f6")
            style.configure("Header.TFrame", background="#ffffff")
            style.configure("Card.TFrame", background="#ffffff", relief="flat")
            style.configure("Title.TLabel", background="#ffffff", foreground="#c8102e", font=("Segoe UI", 24, "bold"))
            style.configure("Subtitle.TLabel", background="#ffffff", foreground="#5a5a5a", font=("Segoe UI", 10))
            style.configure("Section.TLabel", background="#ffffff", foreground="#8a8a8a", font=("Segoe UI", 9, "bold"))
            style.configure("Question.TLabel", background="#ffffff", foreground="#151515", font=("Segoe UI", 20, "bold"))
            style.configure("Hint.TLabel", background="#ffffff", foreground="#4a4a4a", font=("Segoe UI", 11))
            style.configure("Status.TLabel", background="#f4f5f6", foreground="#666666", font=("Segoe UI", 10))
            style.configure("Accent.TButton", background="#c8102e", foreground="#ffffff", font=("Segoe UI", 10, "bold"))
            style.map("Accent.TButton", background=[("active", "#a60f26")], foreground=[("disabled", "#f0f0f0")])
            style.configure("TButton", padding=(14, 10), font=("Segoe UI", 10))
            style.configure("TCombobox", padding=8)
            style.configure("Horizontal.TProgressbar", troughcolor="#e9e9e9", background="#c8102e", bordercolor="#d9d9d9")
            style.configure("CardHeader.TLabel", background="#ffffff", foreground="#1f1f1f", font=("Segoe UI", 13, "bold"))
            style.configure("MetricLabel.TLabel", background="#f8f8f8", foreground="#666666", font=("Segoe UI", 9))
            style.configure("MetricValue.TLabel", background="#f8f8f8", foreground="#1f1f1f", font=("Segoe UI", 14, "bold"))

        def _build_header(self) -> None:
            header = ttk.Frame(self.root, style="Header.TFrame", padding=(18, 16))
            header.pack(fill="x", padx=18, pady=(18, 10))

            left = ttk.Frame(header, style="Header.TFrame")
            left.pack(side="left", fill="x", expand=True)

            ttk.Label(left, text="Aero DSS", style="Title.TLabel").pack(anchor="w")
            ttk.Label(left, text="Simple assistant-style aviation decision wizard.", style="Subtitle.TLabel").pack(anchor="w", pady=(2, 0))

            right = ttk.Frame(header, style="Header.TFrame")
            right.pack(side="right")

            self.preset_combo = ttk.Combobox(
                right,
                textvariable=self.preset_var,
                values=["Load preset", *GUI_PRESETS.keys()],
                state="readonly",
                width=22,
            )
            self.preset_combo.current(0)
            self.preset_combo.pack(side="left", padx=(0, 10))
            self.preset_combo.bind("<<ComboboxSelected>>", self._on_preset_selected)

            self.fullscreen_button = ttk.Button(right, text="Exit fullscreen", command=self._toggle_fullscreen)
            self.fullscreen_button.pack(side="left")

            self.progress = ttk.Progressbar(right, orient="horizontal", mode="determinate", maximum=len(QUESTIONS), variable=self.progress_var, length=220)
            self.progress.pack(side="left", padx=(12, 0))

        def _build_step_rail(self) -> None:
            rail_outer = ttk.Frame(self.root, style="App.TFrame")
            rail_outer.pack(fill="x", padx=18, pady=(0, 10))

            self.step_canvas = tk.Canvas(rail_outer, height=56, bg="#f4f5f6", highlightthickness=0)
            self.step_scroll = ttk.Scrollbar(rail_outer, orient="horizontal", command=self.step_canvas.xview)
            self.step_canvas.configure(xscrollcommand=self.step_scroll.set)
            self.step_canvas.pack(fill="x", expand=True)
            self.step_scroll.pack(fill="x")

            self.step_inner = ttk.Frame(self.step_canvas, style="App.TFrame")
            self.step_window = self.step_canvas.create_window((0, 0), window=self.step_inner, anchor="nw")
            self.step_inner.bind("<Configure>", lambda _event: self.step_canvas.configure(scrollregion=self.step_canvas.bbox("all")))
            self.step_canvas.bind("<Configure>", lambda event: self.step_canvas.itemconfigure(self.step_window, height=56))

            self.step_labels: List[tk.Button] = []
            for index, question in enumerate(QUESTIONS, start=1):
                label = tk.Button(
                    self.step_inner,
                    text=f"{index}. {QUESTION_UI[question.key][0]}",
                    bg="#f2f2f2",
                    fg="#666666",
                    padx=12,
                    pady=8,
                    bd=1,
                    relief="solid",
                    font=("Segoe UI", 10, "bold"),
                    activebackground="#eaeaea",
                    activeforeground="#666666",
                    cursor="hand2",
                    command=lambda step=index - 1: self.go_to_step(step),
                )
                label.pack(side="left", padx=(0, 8), pady=6)
                self.step_labels.append(label)

        def _build_main_area(self) -> None:
            self.main_area = ttk.Frame(self.root, style="App.TFrame")
            self.main_area.pack(fill="both", expand=True, padx=18, pady=(0, 10))

            self.question_card = ttk.Frame(self.main_area, style="Card.TFrame", padding=24)
            self.question_card.pack(fill="both", expand=True)

            self.question_body = ttk.Frame(self.question_card, style="Card.TFrame")
            self.question_body.pack(fill="both", expand=True)

            self.section_label = ttk.Label(self.question_body, style="Section.TLabel", justify="center")
            self.section_label.pack(anchor="center")

            self.question_title = ttk.Label(self.question_body, style="Question.TLabel", wraplength=460, justify="center")
            self.question_title.pack(anchor="center", pady=(8, 0), fill="x")

            self.question_hint = ttk.Label(self.question_body, style="Hint.TLabel", wraplength=480, justify="center")
            self.question_hint.pack(anchor="center", pady=(8, 20), fill="x")

            self.control_frame = ttk.Frame(self.question_body, style="Card.TFrame")
            self.control_frame.pack(anchor="center", pady=(4, 0))

            self.current_widget: Any = None

            self.result_container = ttk.Frame(self.main_area, style="Card.TFrame", padding=18)

            self.result_header = ttk.Label(self.result_container, style="CardHeader.TLabel")
            self.result_header.pack(anchor="w")

            self.result_hero = tk.Frame(self.result_container, bg="#ffffff", bd=1, relief="solid", highlightbackground="#dddddd")
            self.result_hero.pack(fill="x", pady=(10, 10))

            hero_top = tk.Frame(self.result_hero, bg="#ffffff")
            hero_top.pack(fill="x", padx=14, pady=(12, 6))
            self.result_hero_icon = tk.Label(
                hero_top,
                text="✓",
                bg="#eaf7ef",
                fg="#1f7a3d",
                font=("Segoe UI", 14, "bold"),
                width=2,
                height=1,
            )
            self.result_hero_icon.pack(side="left")

            hero_text = tk.Frame(hero_top, bg="#ffffff")
            hero_text.pack(side="left", fill="x", expand=True, padx=10)
            self.result_hero_title = tk.Label(hero_text, text="Evaluation result", bg="#ffffff", fg="#1f1f1f", font=("Segoe UI", 16, "bold"))
            self.result_hero_title.pack(anchor="w")
            self.result_hero_summary = tk.Label(
                hero_text,
                text="Review decision context, sustainability impact, and applied outputs.",
                bg="#ffffff",
                fg="#555555",
                font=("Segoe UI", 10),
                wraplength=760,
                justify="left",
            )
            self.result_hero_summary.pack(anchor="w", pady=(2, 0))

            self.result_hero_pill = tk.Label(
                hero_top,
                text="Ready",
                bg="#f7f7f7",
                fg="#444444",
                padx=10,
                pady=4,
                font=("Segoe UI", 9, "bold"),
                relief="solid",
                bd=1,
            )
            self.result_hero_pill.pack(side="right")

            self.result_summary = ttk.Label(self.result_container, style="Subtitle.TLabel", wraplength=1200, justify="left")
            self.result_summary.pack(anchor="w", pady=(4, 10))

            self.result_debrief = ttk.Frame(self.result_container, style="Card.TFrame")
            self.result_debrief.pack(fill="x", pady=(0, 12))

            self.result_scroll = ScrollableFrame(self.result_container, height=400)
            self.result_scroll.pack(fill="both", expand=True)

        def _build_footer(self) -> None:
            footer = ttk.Frame(self.root, style="Header.TFrame", padding=(18, 14))
            footer.pack(fill="x", padx=18, pady=(0, 18))

            self.step_status = ttk.Label(footer, textvariable=self.status_var, style="Status.TLabel")
            self.step_status.pack(side="left")

            spacer = ttk.Frame(footer, style="Header.TFrame")
            spacer.pack(side="left", fill="x", expand=True)

            self.back_button = ttk.Button(footer, text="Back", command=self.go_back)
            self.back_button.pack(side="left", padx=(0, 8))
            self.next_button = ttk.Button(footer, text="Next", command=self.go_next, style="Accent.TButton")
            self.next_button.pack(side="left", padx=(0, 8))
            self.reset_button = ttk.Button(footer, text="Reset", command=lambda: self._apply_values(FlightContext()))
            self.reset_button.pack(side="left")

        def _bind_shortcuts(self) -> None:
            self.root.bind("<Escape>", lambda _event: self._set_fullscreen(False))
            self.root.bind("<F11>", lambda _event: self._toggle_fullscreen())
            self.root.bind("<Alt-Left>", lambda _event: self.go_back())
            self.root.bind("<Alt-Right>", lambda _event: self.go_next())
            self.root.bind("<Control-Return>", lambda _event: self.go_next())
            self.root.bind("<Control-KP_Enter>", lambda _event: self.go_next())

        def _set_fullscreen(self, enabled: bool) -> None:
            self.fullscreen_state = enabled
            self.root.attributes("-fullscreen", enabled)
            if not enabled:
                self.root.geometry(f"{DEFAULT_WINDOW_WIDTH}x{DEFAULT_WINDOW_HEIGHT}")
            self.fullscreen_button.config(text="Exit fullscreen" if enabled else "Fullscreen")

        def _toggle_fullscreen(self) -> None:
            self._set_fullscreen(not self.fullscreen_state)

        def _handle_window_resize(self, _event: Any = None) -> None:
            card_width = max(340, self.question_card.winfo_width() - 140)
            wrap = min(480, card_width)
            self.question_title.configure(wraplength=wrap)
            self.question_hint.configure(wraplength=min(520, wrap + 20))

        def _apply_values(self, context: FlightContext) -> None:
            self.values = asdict(context)
            self.current_index = 0
            self.current_decisions = []
            self.current_summary = {}
            self.applied_estimates = {}
            self._show_question(0)
            self._refresh_step_bar()

        def _on_preset_selected(self, _event: Any = None) -> None:
            key = self.preset_var.get()
            preset = GUI_PRESETS.get(key)
            if preset is None:
                return
            self._apply_values(preset)

        def _clear_container(self, frame: tk.Widget) -> None:
            for child in frame.winfo_children():
                child.destroy()

        def _render_applied_output(self) -> None:
            if self.applied_output_card is not None:
                try:
                    self.applied_output_card.destroy()
                except Exception:
                    pass
            self.applied_output_card = tk.Frame(self.result_scroll.content, bg="#ffffff", bd=1, relief="solid", highlightbackground="#dddddd")
            self.applied_output_card.pack(fill="x", expand=True, pady=(14, 8))

            header = tk.Frame(self.applied_output_card, bg="#ffffff")
            header.pack(fill="x", padx=14, pady=(12, 4))
            tk.Label(
                header,
                text="♻ Final output",
                bg="#ffffff",
                fg="#1f1f1f",
                font=("Segoe UI", 13, "bold"),
            ).pack(side="left")

            applied_count = len(self.applied_estimates)
            total_fuel = sum(item["fuel_saved_kg"] for item in self.applied_estimates.values())
            total_co2 = sum(item["co2_prevented_kg"] for item in self.applied_estimates.values())

            summary_text = (
                "This output reflects decisions that were logged as Applied in the current session."
                if applied_count
                else "No applied actions logged yet. Save a decision as Applied to populate this output."
            )
            tk.Label(
                self.applied_output_card,
                text=summary_text,
                bg="#ffffff",
                fg="#444444",
                wraplength=1180,
                justify="left",
            ).pack(anchor="w", padx=14, pady=(0, 10))

            metrics = tk.Frame(self.applied_output_card, bg="#f8f8f8")
            metrics.pack(fill="x", padx=14, pady=(0, 12))
            for col, (label_text, value_text) in enumerate(
                [
                    ("✓ Applied actions", str(applied_count)),
                    ("⛽ Estimated fuel saving", f"{total_fuel:.0f} kg"),
                    ("♻ CO2 prevented", f"{total_co2:.1f} kg"),
                ]
            ):
                box = tk.Frame(metrics, bg="#f8f8f8", bd=0)
                box.grid(row=0, column=col, sticky="ew", padx=8, pady=8)
                metrics.grid_columnconfigure(col, weight=1)
                tk.Label(box, text=label_text, bg="#f8f8f8", fg="#666666", font=("Segoe UI", 9)).pack(anchor="w")
                tk.Label(box, text=value_text, bg="#f8f8f8", fg="#1f1f1f", font=("Segoe UI", 14, "bold")).pack(anchor="w")

        def _show_question(self, index: int) -> None:
            self.current_index = index
            self.progress_var.set(min(index, len(QUESTIONS)))
            self._refresh_step_bar()
            self.result_container.pack_forget()
            self.question_card.pack(fill="both", expand=True)
            question = QUESTIONS[index]

            self.section_label.config(text=question.section.upper())
            self.question_title.config(text=QUESTION_UI[question.key][0])
            self.question_hint.config(text=QUESTION_UI[question.key][1])
            self._clear_container(self.control_frame)

            if question.kind == "bool":
                self.current_var = tk.BooleanVar(value=bool(self.values[question.key]))
                widget = ttk.Checkbutton(self.control_frame, text="Enabled", variable=self.current_var)
                widget.pack(anchor="center")
                self.current_widget = widget
            elif question.kind == "choice":
                self.current_var = tk.StringVar(value=str(self.values[question.key]))
                widget = ttk.Combobox(self.control_frame, textvariable=self.current_var, values=question.choices, state="readonly", width=40)
                widget.pack(anchor="center", pady=(0, 4))
                self.current_widget = widget
            elif question.kind == "int":
                self.current_var = tk.IntVar(value=int(self.values[question.key]))
                widget = tk.Spinbox(
                    self.control_frame,
                    from_=int(question.minimum if question.minimum is not None else 0),
                    to=int(question.maximum if question.maximum is not None else 9999),
                    textvariable=self.current_var,
                    width=24,
                    justify="center",
                    font=("Segoe UI", 11),
                    relief="flat",
                    bd=1,
                    buttonbackground="#f3e3e7",
                    background="#ffffff",
                    foreground="#151515",
                    highlightthickness=1,
                    highlightbackground="#d9d9d9",
                    highlightcolor="#c8102e",
                    activebackground="#e8cfd6",
                )
                widget.pack(anchor="center")
                self.current_widget = widget
            elif question.kind == "float":
                self.current_var = tk.DoubleVar(value=float(self.values[question.key]))
                widget = tk.Spinbox(
                    self.control_frame,
                    from_=float(question.minimum if question.minimum is not None else 0.0),
                    to=float(question.maximum if question.maximum is not None else 9999.0),
                    increment=0.5,
                    textvariable=self.current_var,
                    width=24,
                    justify="center",
                    font=("Segoe UI", 11),
                    relief="flat",
                    bd=1,
                    buttonbackground="#f3e3e7",
                    background="#ffffff",
                    foreground="#151515",
                    highlightthickness=1,
                    highlightbackground="#d9d9d9",
                    highlightcolor="#c8102e",
                    activebackground="#e8cfd6",
                )
                widget.pack(anchor="center")
                self.current_widget = widget
            else:
                self.current_var = tk.StringVar(value=str(self.values[question.key]))
                widget = ttk.Entry(self.control_frame, textvariable=self.current_var, width=40, justify="center")
                widget.pack(anchor="center")
                self.current_widget = widget

            ttk.Label(self.question_card, text="Use Back / Next to move through the assistant.", style="Hint.TLabel").pack_forget()
            self.status_var.set(f"Step {index + 1} of {len(QUESTIONS)}")
            try:
                self.current_widget.focus_set()
            except Exception:
                pass
            self._handle_window_resize()
            self._sync_buttons()

        def _refresh_step_bar(self) -> None:
            for position, label in enumerate(self.step_labels):
                if position < self.current_index:
                    label.configure(bg="#eadfe2", fg="#7a0014", activebackground="#eadfe2", activeforeground="#7a0014", text=f"✓ {position + 1}. {QUESTION_UI[QUESTIONS[position].key][0]}")
                elif position == self.current_index:
                    label.configure(bg="#f4d9de", fg="#6b0012", activebackground="#f4d9de", activeforeground="#6b0012", text=f"{position + 1}. {QUESTION_UI[QUESTIONS[position].key][0]}")
                    self.step_canvas.xview_moveto(max(0, position / max(1, len(self.step_labels))))
                else:
                    label.configure(bg="#f2f2f2", fg="#666666", activebackground="#eaeaea", activeforeground="#666666", text=f"{position + 1}. {QUESTION_UI[QUESTIONS[position].key][0]}")

        def _sync_buttons(self) -> None:
            self.back_button.config(state=("normal" if self.current_index > 0 else "disabled"))
            if self.current_index >= len(QUESTIONS) - 1:
                self.next_button.config(text="Evaluate")
            else:
                self.next_button.config(text="Next")

        def _commit_current_value(self) -> None:
            question = QUESTIONS[self.current_index]
            value = self.current_var.get()
            if question.kind == "int":
                try:
                    value = int(value)
                except Exception:
                    value = int(question.default)
            elif question.kind == "float":
                try:
                    value = float(value)
                except Exception:
                    value = float(question.default)
            elif question.kind == "bool":
                value = bool(value)
            self.values[question.key] = value

        def go_back(self) -> None:
            if self.result_container.winfo_ismapped():
                self.result_container.pack_forget()
                self.question_card.pack(fill="both", expand=True)
                self._show_question(len(QUESTIONS) - 1)
                return
            if self.current_index <= 0:
                return
            self._commit_current_value()
            self._show_question(self.current_index - 1)

        def go_to_step(self, step_index: int) -> None:
            if step_index < 0 or step_index >= len(QUESTIONS):
                return
            if self.result_container.winfo_ismapped():
                self.result_container.pack_forget()
                self.question_card.pack(fill="both", expand=True)
            self._commit_current_value()
            self._show_question(step_index)

        def go_next(self) -> None:
            if self.result_container.winfo_ismapped():
                self._evaluate_and_render()
                return
            self._commit_current_value()
            if self.current_index >= len(QUESTIONS) - 1:
                self._evaluate_and_render()
                return
            self._show_question(self.current_index + 1)

        def _current_context(self) -> FlightContext:
            return parse_context(self.values)

        def _evaluate_and_render(self) -> None:
            self._commit_current_value()
            context = self._current_context()
            self.current_decisions = evaluate_all(context)
            self.current_summary = scenario_summary(self.current_decisions, context)

            self.question_card.pack_forget()
            self.result_container.pack(fill="both", expand=True)
            self.result_header.config(text="Evaluation result")
            if self.current_summary.get("overall_state") == "SYSTEM SILENCED":
                hero_visual = verdict_visual("SUPPRESSED")
                hero_pill_text = "System silenced"
            elif self.current_summary["not_recommend"] > self.current_summary["recommended"] and self.current_summary["not_recommend"] >= self.current_summary["conditional"]:
                hero_visual = verdict_visual("DO_NOT_RECOMMEND")
                hero_pill_text = "Operational caution"
            elif self.current_summary["recommended"] >= self.current_summary["not_recommend"]:
                hero_visual = verdict_visual("RECOMMEND")
                hero_pill_text = "Recommended profile"
            else:
                hero_visual = verdict_visual("CONDITIONAL")
                hero_pill_text = "Conditional review"
            self.result_hero_icon.config(text=hero_visual["icon"], bg=hero_visual["bg"], fg=hero_visual["accent"])
            self.result_hero_title.config(text=f"{self.current_summary['overall_state'].title()} overview")
            self.result_hero_summary.config(
                text=(
                    f"Flight {context.flight_id} · {context.aircraft_type} · Phase {context.phase}\n"
                    f"Average confidence {self.current_summary['average_confidence']}% · "
                    f"Fuel {self.current_summary['estimated_fuel_kg']} kg · CO2 {self.current_summary['estimated_co2_kg']} kg"
                )
            )
            self.result_hero_pill.config(
                text=f"{hero_pill_text} · ✓ {self.current_summary['recommended']} recommended",
                bg=hero_visual["bg"],
                fg=hero_visual["accent"],
                highlightbackground=hero_visual["accent"],
            )
            self.result_summary.config(
                text=(
                    f"Flight ID: {context.flight_id} | Aircraft: {context.aircraft_type} | Phase: {context.phase} | "
                    f"Average confidence: %{self.current_summary['average_confidence']} | Fuel savings: {self.current_summary['estimated_fuel_kg']} kg | "
                    f"CO2 prevented: {self.current_summary['estimated_co2_kg']} kg"
                )
            )

            for child in self.result_debrief.winfo_children():
                child.destroy()
            for line in [
                f"Overall state: {self.current_summary['overall_state']}",
                f"Recommended: {self.current_summary['recommended']} | Conditional: {self.current_summary['conditional']} | Not recommended: {self.current_summary['not_recommend']} | Silent: {self.current_summary['suppressed']}",
                "Final responsibility always remains with the flight crew.",
            ]:
                ttk.Label(self.result_debrief, text=line, style="Subtitle.TLabel", wraplength=1200, justify="left").pack(anchor="w", pady=2)

            for child in self.result_scroll.content.winfo_children():
                child.destroy()
            self.result_cards = []
            for decision in self.current_decisions:
                card = tk.Frame(self.result_scroll.content, bg="#ffffff", bd=1, relief="solid", highlightbackground="#dddddd")
                card.pack(fill="x", expand=True, pady=8)
                card.grid_columnconfigure(1, weight=1)

                header = tk.Frame(card, bg="#ffffff")
                header.pack(fill="x", padx=14, pady=(12, 4))
                verdict_style = verdict_visual(decision["verdict_key"])
                tk.Label(
                    header,
                    text=verdict_style["icon"],
                    bg=verdict_style["bg"],
                    fg=verdict_style["accent"],
                    font=("Segoe UI", 12, "bold"),
                    width=2,
                    relief="solid",
                    bd=1,
                    highlightbackground=verdict_style["border"],
                ).pack(side="left", padx=(0, 8))
                title_col = tk.Frame(header, bg="#ffffff")
                title_col.pack(side="left", fill="x", expand=True)
                tk.Label(title_col, text=decision["name"], bg="#ffffff", fg="#1f1f1f", font=("Segoe UI", 13, "bold")).pack(anchor="w")
                tk.Label(title_col, text=f"Decision key: {decision['key']}", bg="#ffffff", fg="#666666", font=("Segoe UI", 9)).pack(anchor="w")
                status = tk.Label(
                    header,
                    text=decision['verdict'],
                    bg=verdict_style["bg"],
                    fg=verdict_style["accent"],
                    padx=10,
                    pady=4,
                    font=("Segoe UI", 9, "bold"),
                    relief="solid",
                    bd=1,
                    highlightbackground=verdict_style["border"],
                )
                status.pack(side="right")

                metrics = tk.Frame(card, bg="#f8f8f8")
                metrics.pack(fill="x", padx=14, pady=(0, 10))
                for col, (label_text, value_text) in enumerate(
                    [
                        ("✓ Confidence", f"%{decision['confidence']}"),
                        ("⛽ Fuel saving", f"{decision['fuel_saved_kg_estimate']:.0f} kg"),
                        ("♻ CO2 prevented", f"{decision['co2_prevented_kg_estimate']:.1f} kg"),
                    ]
                ):
                    box = tk.Frame(metrics, bg="#f8f8f8", bd=0)
                    box.grid(row=0, column=col, sticky="ew", padx=8, pady=8)
                    metrics.grid_columnconfigure(col, weight=1)
                    tk.Label(box, text=label_text, bg="#f8f8f8", fg="#666666", font=("Segoe UI", 9)).pack(anchor="w")
                    tk.Label(box, text=value_text, bg="#f8f8f8", fg="#1f1f1f", font=("Segoe UI", 14, "bold")).pack(anchor="w")

                progress = ttk.Progressbar(card, value=decision["confidence"], maximum=100, mode="determinate")
                progress.pack(fill="x", padx=14, pady=(0, 10))

                def _block(parent: tk.Widget, title: str, items: List[str]) -> None:
                    tk.Label(parent, text=title, bg="#ffffff", fg="#1f1f1f", font=("Segoe UI", 10, "bold")).pack(anchor="w", padx=14, pady=(2, 0))
                    if items:
                        for item in items:
                            tk.Label(parent, text=f"• {item}", bg="#ffffff", fg="#444444", wraplength=1180, justify="left").pack(anchor="w", padx=24, pady=1)
                    else:
                        tk.Label(parent, text="• None", bg="#ffffff", fg="#444444").pack(anchor="w", padx=24, pady=1)

                _block(card, "Reasons", decision["reasons"])
                _block(card, "Notes / constraints", decision["caveats"])

                form = tk.Frame(card, bg="#ffffff")
                form.pack(fill="x", padx=14, pady=12)
                choice_var = tk.StringVar(value=PilotChoice.NO_LOG.name)
                choice_combo = ttk.Combobox(form, values=[choice.name for choice in PilotChoice], state="readonly", textvariable=choice_var, width=16)
                choice_combo.set(PilotChoice.NO_LOG.name)
                choice_combo.pack(side="left")
                note_var = tk.StringVar()
                note_entry = ttk.Entry(form, textvariable=note_var)
                note_entry.pack(side="left", fill="x", expand=True, padx=10)
                status_var = tk.StringVar(value="No log yet.")

                def save_current_log(decision_key: str = decision["key"], choice_holder=choice_var, note_holder=note_var, status_holder=status_var) -> None:
                    choice_name = choice_holder.get()
                    if choice_name == PilotChoice.NO_LOG.name:
                        status_holder.set("Log skipped.")
                        return
                    ctx = self._current_context()
                    decision_data = next((item for item in self.current_decisions if item["key"] == decision_key), None)
                    if decision_data is None:
                        status_holder.set("Could not find decision.")
                        return
                    log_decision(ctx, decision_data, PilotChoice[choice_name].value, note_holder.get().strip())
                    if choice_name == PilotChoice.APPLIED.name:
                        self.applied_estimates[decision_key] = decision_impact_estimate(decision_key, ctx)
                        impact = self.applied_estimates[decision_key]
                        self._render_applied_output()
                        status_holder.set(
                            f"Saved to CSV. Estimated fuel saving: {impact['fuel_saved_kg']:.0f} kg | "
                            f"CO2 prevented: {impact['co2_prevented_kg']:.1f} kg."
                        )
                    else:
                        self.applied_estimates.pop(decision_key, None)
                        self._render_applied_output()
                        status_holder.set("Saved to CSV.")

                ttk.Button(form, text="Save log", style="Accent.TButton", command=save_current_log).pack(side="right")
                ttk.Label(card, textvariable=status_var, style="Subtitle.TLabel").pack(anchor="w", padx=14, pady=(0, 12))
                self.result_cards.append(card)

            self._render_applied_output()

            self.status_var.set("Evaluation complete. Review the result cards below.")
            self._sync_buttons()

        def run(self) -> None:
            self.root.mainloop()

    WizardApp().run()


def print_intro() -> None:
    clear_screen()
    banner(APP_NAME)
    print("The wizard UI opens by default.")
    print("Use `--cli` if you want the terminal flow instead.")
    print("Questions advance one by one, with back navigation and a final result screen.\n")


def run_cli() -> None:
    print_intro()
    while True:
        ctx = ask_questions()
        if ctx is None:
            break
        review_loop(ctx)
        if not ask_yes_no("\nWould you like to evaluate a new scenario?", False):
            print("\nProgram ended. Safe flights.")
            break


def main() -> None:
    if "--cli" in sys.argv:
        run_cli()
        return

    if not PYQT_AVAILABLE:
        run_gui()
        return

    run_gui()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nProgram stopped by the user.")
