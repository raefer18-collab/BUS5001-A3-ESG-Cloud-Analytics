"""Builds the EcoAssist ESG Incident Reporter as a Dialogflow CX JSON package (zip).

The zip can be restored into a Conversational Agents (Dialogflow CX) agent via
Agent settings > Restore. Run:  python build_agent.py
"""
import json
import os
import shutil
import uuid
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "agent_package")
ZIP = os.path.join(HERE, "EcoAssist_agent.zip")
NS = uuid.UUID("6905d64c-ca60-481a-bfd2-9c27162ca04b")
FLOW = "Default Start Flow"

shutil.rmtree(OUT, ignore_errors=True)


def uid(key):
    return str(uuid.uuid5(NS, key))


def write(rel, data):
    path = os.path.join(OUT, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def msg(*texts):
    # One message per sentence: several strings inside a single text message are
    # treated by Dialogflow as random alternatives, not as consecutive replies.
    return {"messages": [{"text": {"text": [t]}, "languageCode": "en"} for t in texts]}


# Short report reference such as ESG-3F9A1C, generated without a webhook.
NEW_REF = "$sys.func.UPPER($sys.func.MID($sys.func.UUID(), 1, 6))"


def route(key, target=None, intent=None, condition=None, say=None, set_params=None):
    r = {"name": uid("route:" + key)}
    if intent:
        r["intent"] = intent
    if condition:
        r["condition"] = condition
    ful = msg(say) if say else {}
    if set_params:
        ful["setParameterActions"] = [{"parameter": k, "value": v} for k, v in set_params.items()]
    if ful:
        r["triggerFulfillment"] = ful
    if target:
        r["targetPage"] = target
    return r


def handler(key, event, say, target=None):
    h = {"name": uid("evt:" + key), "event": event, "triggerFulfillment": msg(say)}
    if target:
        h["targetPage"] = target
    return h


def param(name, entity, prompt, reprompts=(), redact=False):
    p = {
        "displayName": name,
        "entityType": entity,
        "required": True,
        "fillBehavior": {
            "initialPromptFulfillment": msg(prompt),
            "repromptEventHandlers": [
                handler(f"{name}:{ev}", ev, text) for ev, text in reprompts
            ],
        },
    }
    if redact:
        p["redact"] = True
    return p


def page(name, entry=None, params=None, routes=(), events=()):
    p = {"name": uid("page:" + name), "displayName": name}
    if entry:
        p["entryFulfillment"] = msg(entry) if isinstance(entry, str) else entry
    if params:
        p["form"] = {"parameters": params}
    p["transitionRoutes"] = list(routes)
    p["eventHandlers"] = list(events)
    write(f"flows/{FLOW}/pages/{name}.json", p)


FINAL = '$page.params.status = "FINAL"'

# ---------------------------------------------------------------- entities
ENTITIES = {
    "incident_type": [
        ("water_leak", ["water leak", "leak", "leaking", "burst pipe", "dripping tap", "running tap",
                        "flooding", "water running", "toilet running", "pipe leak"]),
        ("energy_waste", ["energy waste", "lights left on", "air conditioning running", "aircon on overnight",
                          "heating left on", "computers left on", "power waste", "air conditioning",
                          "lights on", "energy"]),
        ("waste_contamination", ["recycling contamination", "contaminated recycling", "bins contaminated",
                                 "wrong bin", "overflowing bins", "rubbish", "waste", "recycling",
                                 "illegal dumping", "littering"]),
        ("hazardous_spill", ["chemical spill", "oil spill", "hazardous spill", "hazardous waste", "battery leak",
                             "fuel leak", "asbestos", "unsafe disposal", "spill", "toxic"]),
        ("accessibility_barrier", ["accessibility barrier", "blocked ramp", "blocked accessible entrance",
                                   "lift not working", "broken elevator", "accessible toilet", "ramp blocked",
                                   "wheelchair access", "accessible entrance blocked", "accessibility"]),
        ("other", ["other", "something else", "not sure", "different issue"]),
    ],
    "risk_level": [
        ("immediate_danger", ["immediate danger", "danger", "dangerous", "someone is hurt", "injury", "unsafe",
                              "emergency", "safety risk", "electrical hazard", "fire", "people at risk"]),
        ("ongoing_damage", ["ongoing damage", "still running", "getting worse", "ongoing", "spreading",
                            "damage", "all day", "continuous", "still happening"]),
        ("no_immediate_risk", ["no immediate risk", "no risk", "not urgent", "minor", "no", "nope",
                               "not dangerous", "it's fine", "low"]),
    ],
    "contact_pref": [
        ("updates_requested", ["keep me updated", "update me", "contact me", "email me", "yes please",
                        "send me updates", "notify me", "yes"]),
        ("anonymous", ["anonymous", "stay anonymous", "don't contact me", "no thanks", "no updates",
                       "no contact", "anonymously", "no"]),
    ],
    "guidance_topic": [
        ("recycling", ["recycling", "recycle", "which bin", "soft plastics", "cardboard", "coffee cups", "bins"]),
        ("energy_saving", ["energy saving", "save energy", "reduce energy", "electricity", "turn off lights",
                           "air conditioning settings", "power"]),
        ("water_saving", ["water saving", "save water", "reduce water", "water use"]),
        ("hazardous_waste", ["hazardous waste", "batteries", "e-waste", "chemicals", "printer cartridges",
                             "light globes", "electronic waste"]),
    ],
}

for name, values in ENTITIES.items():
    write(f"entityTypes/{name}/{name}.json", {
        "name": uid("entity:" + name), "displayName": name, "kind": "KIND_MAP",
        "autoExpansionMode": "AUTO_EXPANSION_MODE_DEFAULT", "enableFuzzyExtraction": True,
    })
    write(f"entityTypes/{name}/entities/en.json", {"entities": [
        {"value": v.replace("_", " "),
         "synonyms": list(dict.fromkeys([v.replace("_", " ")] + syns)), "languageCode": "en"}
        for v, syns in values
    ]})

write("entityTypes/report_ref/report_ref.json", {
    "name": uid("entity:report_ref"), "displayName": "report_ref", "kind": "KIND_REGEXP",
})
write("entityTypes/report_ref/entities/en.json", {"entities": [
    {"value": r"ESG-?[A-Za-z0-9]{4,8}", "synonyms": [r"ESG-?[A-Za-z0-9]{4,8}"], "languageCode": "en"},
]})

# ----------------------------------------------------------------- intents


def tp(text):
    """'There is a [water leak](incident_type) in C' -> annotated parts."""
    parts, i = [], 0
    while i < len(text):
        s = text.find("[", i)
        if s == -1:
            parts.append({"text": text[i:]})
            break
        if s > i:
            parts.append({"text": text[i:s]})
        e = text.index("]", s)
        p_s = text.index("(", e)
        p_e = text.index(")", p_s)
        parts.append({"text": text[s + 1:e], "parameterId": text[p_s + 1:p_e]})
        i = p_e + 1
    return parts


def intent(name, phrases, params=None, iid=None, desc=""):
    data = {"name": iid or uid("intent:" + name), "displayName": name, "priority": 500000}
    if desc:
        data["description"] = desc
    if params:
        data["parameters"] = [{"id": k, "entityType": v} for k, v in params.items()]
    write(f"intents/{name}/{name}.json", data)
    if phrases:
        write(f"intents/{name}/trainingPhrases/en.json", {"trainingPhrases": [
            {"id": uid(f"tp:{name}:{p}"), "parts": tp(p), "repeatCount": 1, "languageCode": "en"} for p in phrases
        ]})


intent("Default Welcome Intent", ["hi", "hello", "hey", "good morning", "start", "hi EcoAssist",
                                  "hello there", "I need some help", "what can you do"],
       iid="00000000-0000-0000-0000-000000000000")
intent("Default Negative Intent", [], iid="ffffffff-ffff-ffff-ffff-ffffffffffff")

intent("report.incident", [
    "I want to report an issue",
    "I need to report a sustainability problem",
    "report a facilities issue",
    "There is a [water leak](incident_type) in Building C",
    "There's a [water leak](incident_type) that has been running all morning",
    "The [air conditioning](incident_type) is running overnight in an empty office",
    "The [lights are left on](incident_type) every night in the library",
    "The [recycling bins are contaminated](incident_type) again",
    "Someone has put rubbish in the [wrong bin](incident_type)",
    "I found a [chemical spill](incident_type) in the lab corridor",
    "There is [hazardous waste](incident_type) dumped behind the car park",
    "The [accessible entrance is blocked](incident_type) near the main building",
    "The [lift is not working](incident_type) in Building A",
    "I want to log a [leak](incident_type)",
    "report [energy waste](incident_type)",
    "report a [spill](incident_type)",
    "I'd like to report an [accessibility barrier](incident_type)",
    "there's a problem I need to report",
    "something is wrong in my building",
    "log a new incident",
], params={"incident_type": "@incident_type"},
    desc="User wants to report an environmental, facilities or accessibility incident.")

intent("get.guidance", [
    "How do I [recycle](guidance_topic) properly?",
    "Which bin do I use for [coffee cups](guidance_topic)?",
    "How can I [save energy](guidance_topic) in the office?",
    "Where do I dispose of [batteries](guidance_topic)?",
    "Tips to [reduce water](guidance_topic) use",
    "what do I do with [e-waste](guidance_topic)",
    "I need sustainability advice",
    "give me sustainability tips",
    "how can I be more sustainable at work",
    "sustainability guidance",
    "what are the [recycling](guidance_topic) rules",
    "how do I get rid of [chemicals](guidance_topic) safely",
], params={"guidance_topic": "@guidance_topic"},
    desc="User wants guidance on recycling, energy, water or hazardous waste.")

intent("check.status", [
    "check my report",
    "what's the status of my report",
    "has my issue been fixed",
    "check report [ESG-4F2A9C](ref_number)",
    "status of [ESG-7B31D0](ref_number)",
    "any update on my incident",
    "follow up on a report I made",
    "track my report",
], params={"ref_number": "@report_ref"},
    desc="User wants to check the status of an existing report.")

intent("escalate.human", [
    "speak to a person",
    "talk to a human",
    "I want to talk to someone",
    "connect me to an agent",
    "this is urgent I need a person",
    "can I speak to facilities",
    "get me a real person",
    "I have a sensitive issue",
    "I want to make a confidential complaint",
    "human please",
    "operator",
], desc="User asks for a human or raises a sensitive matter - always honoured.")

intent("confirm.yes", ["yes", "yeah", "yep", "correct", "that's right", "submit it", "go ahead",
                       "sounds good", "confirm", "yes please submit", "looks good"])
intent("confirm.no", ["no", "nope", "that's wrong", "not right", "change it", "start again",
                      "incorrect", "no that's not correct", "cancel"])
intent("end.conversation", ["bye", "goodbye", "that's all", "no thanks that's all", "thanks bye",
                            "nothing else", "I'm done", "see you", "thank you that's everything"])

# ------------------------------------------------------------------- flow
WELCOME = ("Hi, I'm EcoAssist, the Sustainability Support Assistant. I can help you:\n"
           "1. Report a sustainability or facilities issue\n"
           "2. Get sustainability guidance\n"
           "3. Check the status of a report\n"
           "4. Speak to a person\n"
           "Privacy note: I only ask for what is needed to fix the issue. You do not need to give your name "
           "and you can stay anonymous. What would you like to do?")

flow = {
    "name": "00000000-0000-0000-0000-000000000000",
    "displayName": FLOW,
    "description": "EcoAssist - ESG sustainability incident reporting assistant.",
    "transitionRoutes": [
        route("welcome", intent="Default Welcome Intent", say=WELCOME),
        route("report", "Incident Details", intent="report.incident",
              say="Thanks for helping us run a more sustainable workplace. Let's log this issue."),
        route("guidance", "Sustainability Guidance", intent="get.guidance"),
        route("status", "Check Report Status", intent="check.status"),
        route("human", "Human Handover", intent="escalate.human"),
        route("end", "End Conversation", intent="end.conversation"),
    ],
    "eventHandlers": [
        handler("flow:nm1", "sys.no-match-1",
                "Sorry, I didn't quite understand. You can say: report an issue, sustainability guidance, "
                "check a report, or speak to a person."),
        handler("flow:nm2", "sys.no-match-2",
                "I'm still having trouble understanding. Try a short phrase like 'report a water leak', "
                "or say 'speak to a person' and I'll connect you with the ESG Service Desk."),
        handler("flow:nm3", "sys.no-match-3",
                "I don't want to keep you waiting, so I'm handing you over to a person.", "Human Handover"),
        handler("flow:ni", "sys.no-input-default",
                "Are you still there? Tell me what you'd like to do, or say 'speak to a person'."),
        handler("flow:nmd", "sys.no-match-default",
                "Sorry, I didn't catch that. Could you say it another way?"),
    ],
    "nluSettings": {"modelType": "MODEL_TYPE_ADVANCED", "classificationThreshold": 0.3,
                    "modelTrainingMode": "MODEL_TRAINING_MODE_AUTOMATIC"},
}
write(f"flows/{FLOW}/{FLOW}.json", flow)

# ------------------------------------------------------------------- pages
ANYTHING_ELSE = "Anything Else"

page("Incident Details",
     params=[
         param("incident_type", "@incident_type",
               "What type of issue are you reporting? For example: water leak, energy waste, "
               "recycling contamination, hazardous spill, accessibility barrier, or other.",
               [("sys.no-match-1", "Sorry, I didn't recognise that issue type. Please choose one: water leak, "
                                   "energy waste, recycling contamination, hazardous spill, accessibility "
                                   "barrier, or other."),
                ("sys.no-match-2", "Let's keep it simple - if you're unsure, just say 'other' and describe it "
                                   "to the team later.")]),
         param("location", "@sys.any",
               "Where is the issue? Please include the building and the room or area, "
               "for example 'Building C, level 2 kitchen'."),
         param("risk_level", "@risk_level",
               "Is anyone in danger, or is the issue causing ongoing damage? You can say 'immediate danger', "
               "'ongoing damage' or 'no immediate risk'.",
               [("sys.no-match-1", "Sorry, please answer with 'immediate danger', 'ongoing damage' or "
                                   "'no immediate risk'.")]),
     ],
     routes=[
         route("details:danger", "Emergency Escalation",
               condition=FINAL + ' AND $session.params.risk_level = "immediate danger"',
               set_params={"report_ref": NEW_REF, "assigned_team": "Health, Safety & Environment (HSE)",
                           "priority": "CRITICAL"}),
         route("details:ok", "Contact Preference", condition=FINAL),
     ])

page("Emergency Escalation",
     entry=msg(
         "This sounds urgent. If anyone is injured or in immediate danger, leave the area and call "
         "Campus Security on 1800 555 000 (or 000 for emergencies) now.",
         "I have flagged your $session.params.incident_type report at $session.params.location as CRITICAL "
         "and alerted the on-call $session.params.assigned_team team.",
         "Your reference is ESG-$session.params.report_ref. A team member will follow up within 15 minutes."),
     routes=[route("emerg:end", "End Session", condition="true")])

page("Contact Preference",
     params=[param("contact_pref", "@contact_pref",
                   "Would you like updates on this report, or would you prefer to stay anonymous? "
                   "Say 'keep me updated' or 'anonymous'. Your details are only used to follow up this report.",
                   [("sys.no-match-1", "Please say 'keep me updated' or 'anonymous'.")])],
     routes=[
         route("contact:me", "Collect Contact", condition=FINAL + ' AND $session.params.contact_pref = "updates requested"'),
         route("contact:anon", "Confirm Report", condition=FINAL,
               set_params={"email": "not provided (anonymous)"}),
     ])

page("Collect Contact",
     params=[param("email", "@sys.email", "What email address should we send updates to?",
                   [("sys.no-match-1", "That doesn't look like an email address. Please type it like "
                                       "name@example.com, or say 'speak to a person'.")], redact=True)],
     routes=[route("collect:done", "Confirm Report", condition=FINAL)])

page("Confirm Report",
     entry=("Here is a summary of your report:\n"
            "- Issue: $session.params.incident_type\n"
            "- Location: $session.params.location\n"
            "- Risk: $session.params.risk_level\n"
            "- Updates: $session.params.contact_pref\n"
            "Shall I submit it? Please say yes or no."),
     routes=[
         route("confirm:yes", "Route To Team", intent="confirm.yes"),
         route("confirm:no", "Incident Details", intent="confirm.no",
               say="No problem, let's correct it.",
               set_params={"incident_type": None, "location": None, "risk_level": None,
                           "contact_pref": None, "email": None}),
     ],
     events=[handler("confirm:nm", "sys.no-match-default",
                     "Sorry, please say 'yes' to submit the report or 'no' to change it.")])

TEAMS = [
    ("water_leak", "Facilities Maintenance (Plumbing)", "HIGH"),
    ("energy_waste", "Energy & Sustainability Office", "MEDIUM"),
    ("waste_contamination", "Waste & Recycling Services", "MEDIUM"),
    ("hazardous_spill", "Health, Safety & Environment (HSE)", "HIGH"),
    ("accessibility_barrier", "Accessibility & Inclusion Team", "HIGH"),
]
ONGOING = '$session.params.risk_level = "ongoing damage"'
team_routes = []
for t, team, prio in TEAMS + [("other", "ESG Service Desk", "MEDIUM")]:
    is_type = f'$session.params.incident_type = "{t.replace("_", " ")}"'
    # Ongoing damage always raises priority to HIGH.
    team_routes.append(route(f"team:{t}:ongoing", "Report Submitted", condition=f"{is_type} AND {ONGOING}",
                             set_params={"assigned_team": team, "priority": "HIGH", "report_ref": NEW_REF}))
    team_routes.append(route(f"team:{t}", "Report Submitted", condition=is_type,
                             set_params={"assigned_team": team, "priority": prio, "report_ref": NEW_REF}))
team_routes.append(route("team:fallback", "Report Submitted", condition="true",
                         set_params={"assigned_team": "ESG Service Desk", "priority": "MEDIUM",
                                     "report_ref": NEW_REF}))
page("Route To Team", routes=team_routes)

page("Report Submitted",
     entry=msg(
         "Thank you - your report has been submitted. Your reference is ESG-$session.params.report_ref.",
         "It has been routed to the $session.params.assigned_team team with $session.params.priority priority. "
         "Updates: $session.params.email."),
     routes=[route("submitted:next", ANYTHING_ELSE, condition="true")])

page(ANYTHING_ELSE,
     entry="Is there anything else I can help with? You can report another issue, ask for guidance, "
           "check a report, or say goodbye.",
     events=[handler("else:nm", "sys.no-match-default",
                     "You can say 'report an issue', 'guidance', 'check a report', 'speak to a person' or 'bye'.")])

GUIDANCE = {
    "recycling": "Recycling tips: rinse containers, flatten cardboard, and keep soft plastics and coffee cups "
                 "out of the yellow recycling bin - use the soft-plastics and cup collection points on each level.",
    "energy_saving": "Energy tips: switch off lights and screens when you leave, keep air conditioning between "
                     "21 and 24 degrees, and report rooms heated or cooled overnight so Facilities can fix the schedule.",
    "water_saving": "Water tips: report dripping taps and running toilets straight away, and use the eco setting "
                    "on kitchen dishwashers. A leaking tap can waste over 20,000 litres a year.",
    "hazardous_waste": "Hazardous waste: never put batteries, e-waste, chemicals, globes or printer cartridges in "
                       "general bins. Take them to the hazardous waste drop-off point at Building B reception.",
}
page("Sustainability Guidance",
     params=[param("guidance_topic", "@guidance_topic",
                   "Happy to help. Which topic: recycling, energy saving, water saving, or hazardous waste?",
                   [("sys.no-match-1", "Please choose recycling, energy saving, water saving, or hazardous waste.")])],
     routes=[route(f"guide:{k}", ANYTHING_ELSE,
                   condition=FINAL + f' AND $session.params.guidance_topic = "{k.replace("_", " ")}"', say=v)
             for k, v in GUIDANCE.items()])

page("Check Report Status",
     params=[param("ref_number", "@report_ref",
                   "Sure. What is your report reference? It starts with ESG, for example ESG-4F2A9C.",
                   [("sys.no-match-1", "I couldn't find a reference in that. It looks like ESG followed by "
                                       "4 to 8 letters or numbers.")])],
     routes=[route("status:done", ANYTHING_ELSE, condition=FINAL,
                   say="Report $session.params.ref_number is currently IN PROGRESS with the assigned team. "
                       "You'll receive an update when it is resolved.")])

page("Human Handover",
     entry={"messages": msg(
         "I'll connect you with the ESG Service Desk. Sensitive matters such as safety, conduct or "
         "discrimination concerns are handled confidentially by a trained staff member.",
         "The ESG Service Desk is available Monday to Friday, 8:30am-5pm, on extension 4500 or "
         "esg.servicedesk@example.org. I've shared a summary of this conversation with them.")["messages"] + [
         {"liveAgentHandoff":{"metadata": {"reason": "user_requested_or_repeated_no_match",
                                            "queue": "esg_service_desk"}}, "languageCode": "en"},
     ]},
     routes=[route("human:end", "End Session", condition="true")])

page("End Conversation",
     entry="Thanks for helping make our workplace more sustainable. Goodbye!",
     routes=[route("bye:end", "End Session", condition="true")])

# ------------------------------------------------------------------- agent
write("agent.json", {
    "displayName": "EcoAssist ESG Incident Reporter",
    "defaultLanguageCode": "en",
    "timeZone": "Australia/Sydney",
    "description": "ESG Sustainability Support Assistant - incident reporting prototype (BUS5001 A3).",
    "startFlow": FLOW,
    "enableStackdriverLogging": True,
    "advancedSettings": {"loggingSettings": {"enableStackdriverLogging": True,
                                             "enableInteractionLogging": True}},
})


if __name__ == "__main__":
    if os.path.exists(ZIP):
        os.remove(ZIP)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(OUT):
            for f in files:
                full = os.path.join(root, f)
                z.write(full, os.path.relpath(full, OUT).replace(os.sep, "/"))
    print("Wrote", ZIP)
