"""Generates the report diagrams as PNG files (matplotlib, no external tools)."""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))

C = {  # palette
    "blue": "#dbe9f6", "blue_e": "#2a6f97", "green": "#dff3e4", "green_e": "#2d8a4e",
    "amber": "#fff1d6", "amber_e": "#c98a00", "red": "#fde2e1", "red_e": "#c0392b",
    "grey": "#eeeeee", "grey_e": "#666666", "purple": "#ece4f7", "purple_e": "#6c4bb4",
}


def box(ax, x, y, w, h, text, kind="blue", fs=8.5, bold=False):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=C[kind], ec=C[kind + "_e"], lw=1.4))
    ax.text(x, y, text, ha="center", va="center", fontsize=fs, wrap=True,
            fontweight="bold" if bold else "normal")


def arrow(ax, x1, y1, x2, y2, label="", color="#444444", fs=7, style="-|>", ls="-", rad=0.0, lx=0, ly=0):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color, lw=1.2, ls=ls,
                                connectionstyle=f"arc3,rad={rad}", shrinkA=2, shrinkB=2))
    if label:
        ax.text((x1 + x2) / 2 + lx, (y1 + y2) / 2 + ly, label, fontsize=fs, ha="center", va="center",
                color=color, bbox=dict(fc="white", ec="none", pad=0.6))


def canvas(w, h, title):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, w)
    ax.set_ylim(0, h)
    ax.axis("off")
    ax.set_title(title, fontsize=12, fontweight="bold", loc="left")
    return fig, ax


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, name), dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("saved", name)


def q1_conversation_map():
    fig, ax = canvas(13, 8.6, "Figure: EcoAssist conversation map (Dialogflow CX - Default Start Flow)")
    box(ax, 6.5, 7.9, 3.2, 0.6, "Start Page\nWelcome + privacy notice + menu", "purple", bold=True)
    # intents from start
    box(ax, 1.4, 6.6, 2.2, 0.6, "Sustainability Guidance\nform: guidance_topic", "green")
    box(ax, 4.2, 6.6, 2.2, 0.6, "Check Report Status\nform: ref_number (regex)", "green")
    box(ax, 8.6, 6.6, 2.4, 0.6, "Incident Details\nform: incident_type,\nlocation, risk_level", "blue", bold=True)
    box(ax, 11.6, 6.6, 2.2, 0.6, "Human Handover\nlive-agent handoff", "red")
    arrow(ax, 5.2, 7.65, 1.6, 6.92, "get.guidance", rad=0.1)
    arrow(ax, 5.8, 7.6, 4.3, 6.92, "check.status")
    arrow(ax, 7.2, 7.6, 8.5, 6.92, "report.incident")
    arrow(ax, 8.1, 7.7, 11.5, 6.92, "escalate.human\n(any page)", rad=-0.1)
    # decision
    box(ax, 8.6, 5.3, 2.6, 0.6, "Decision: risk_level?", "amber", bold=True)
    arrow(ax, 8.6, 6.27, 8.6, 5.62, "form FINAL")
    box(ax, 11.6, 5.3, 2.2, 0.7, "Emergency Escalation\nCRITICAL -> HSE on-call\nsafety advice + ref", "red")
    arrow(ax, 9.9, 5.3, 10.5, 5.3, "immediate\ndanger", color=C["red_e"], ly=0.32)
    box(ax, 8.6, 4.1, 2.6, 0.6, "Contact Preference\nform: contact_pref (consent)", "blue")
    arrow(ax, 8.6, 4.98, 8.6, 4.42, "ongoing damage /\nno immediate risk", lx=1.0)
    box(ax, 11.6, 4.1, 2.2, 0.6, "Collect Contact\nform: email (redacted)", "blue")
    arrow(ax, 9.9, 4.1, 10.5, 4.1, "updates\nrequested", ly=0.3)
    box(ax, 8.6, 2.9, 2.6, 0.6, "Confirm Report\nsummary read-back", "amber", bold=True)
    arrow(ax, 8.6, 3.78, 8.6, 3.22, "anonymous")
    arrow(ax, 11.6, 3.78, 9.9, 3.05, "", rad=-0.2)
    arrow(ax, 7.3, 2.9, 7.3, 6.3, "confirm.no\n(clear params, re-ask)", color=C["amber_e"], rad=-0.35, lx=-1.1)
    box(ax, 8.6, 1.75, 2.6, 0.6, "Route To Team\nconditional routes set\nassigned_team, priority, ref", "purple")
    arrow(ax, 8.6, 2.58, 8.6, 2.07, "confirm.yes")
    box(ax, 4.9, 1.75, 2.6, 0.6, "Report Submitted\nreference ESG-XXXXXX\n+ team + priority", "green", bold=True)
    arrow(ax, 7.3, 1.75, 6.2, 1.75)
    box(ax, 1.6, 1.75, 2.4, 0.6, "Anything Else?\n(flow routes in scope)", "grey")
    arrow(ax, 3.6, 1.75, 2.8, 1.75)
    arrow(ax, 1.4, 6.28, 1.5, 2.07, "", rad=0.0)
    arrow(ax, 4.2, 6.28, 2.0, 2.07, "", rad=0.15)
    box(ax, 1.6, 0.55, 2.4, 0.5, "End Conversation -> End Session", "grey")
    arrow(ax, 1.6, 1.45, 1.6, 0.8, "end.conversation")
    box(ax, 11.6, 0.9, 2.6, 1.1, "Flow-level event handlers\nno-match-1: clarify options\nno-match-2: suggest phrasing\nno-match-3: hand to human\nno-input: re-prompt", "grey", fs=7.5)
    arrow(ax, 11.6, 1.45, 11.6, 6.28, "", color=C["red_e"], ls="--", rad=0.25)
    save(fig, "q1_conversation_map.png")


def q1_cloud_workflow():
    fig, ax = canvas(13, 5.2, "Figure: Conceptual cloud-enabled workflow for EcoAssist (Google Cloud)")
    box(ax, 1.2, 3.6, 1.9, 0.9, "Employees\nweb chat / Teams /\nmobile (Dialogflow\nMessenger)", "grey")
    box(ax, 3.7, 3.6, 2.2, 0.9, "Dialogflow CX agent\nEcoAssist\n(intents, forms, routing)", "purple", bold=True)
    box(ax, 6.4, 3.6, 2.2, 0.9, "Webhook\nCloud Run function\n(validate, create ticket)", "blue")
    box(ax, 9.2, 4.4, 2.4, 0.7, "ServiceNow / Jira\nfacilities ticket", "amber")
    box(ax, 9.2, 3.3, 2.4, 0.7, "Pub/Sub topic\n'esg-incidents'", "blue")
    box(ax, 9.2, 2.2, 2.4, 0.7, "On-call alerting\n(SMS / Teams) for CRITICAL", "red")
    box(ax, 11.9, 3.3, 1.8, 0.7, "BigQuery\nESG incident table", "green")
    box(ax, 11.9, 1.9, 1.8, 0.8, "Looker Studio\nESG dashboard\n(GRI 303/306 KPIs)", "green")
    box(ax, 6.4, 1.4, 2.4, 0.9, "Governance layer\nIAM least privilege, DLP\nredaction, Cloud Logging,\nretention policy", "grey", fs=7.5)
    box(ax, 3.7, 1.4, 2.2, 0.9, "Human agents\nESG Service Desk\n(live-agent handoff)", "red")
    arrow(ax, 2.15, 3.6, 2.6, 3.6, "text")
    arrow(ax, 4.8, 3.6, 5.3, 3.6, "params")
    arrow(ax, 7.5, 3.8, 8.0, 4.3)
    arrow(ax, 7.5, 3.5, 8.0, 3.3)
    arrow(ax, 7.5, 3.3, 8.0, 2.3, "priority =\nCRITICAL", fs=6.5, lx=-0.1)
    arrow(ax, 10.4, 3.3, 11.0, 3.3)
    arrow(ax, 11.9, 2.95, 11.9, 2.3)
    arrow(ax, 3.7, 3.15, 3.7, 1.85, "escalate.human /\nno-match-3", lx=0.9)
    arrow(ax, 6.4, 3.15, 6.4, 1.85, "", ls="--", color=C["grey_e"], style="<|-|>")
    save(fig, "q1_cloud_workflow.png")


def q2_attack_chain():
    fig, ax = canvas(13, 4.6, "Figure: Snowflake customer-tenant compromise attack chain (UNC5537, 2024)")
    steps = [
        ("1. Infostealer malware\n(VIDAR, LUMMA, RedLine...)\non contractor/employee PCs\nsince 2020", "red"),
        ("2. Credentials harvested\nusername + password\nsold / shared on\ncriminal markets", "red"),
        ("3. Login to customer\nSnowflake tenant\n(Snowsight / SnowSQL)\nvia Mullvad/PIA VPN", "amber"),
        ("4. No MFA, no network\npolicy, creds unrotated\n(up to 4 years) ->\nlogin succeeds", "amber"),
        ("5. Recon (FROSTBITE),\nSHOW TABLES, SELECT *,\nCOPY INTO temp stage,\nGET -> exfiltrate", "purple"),
        ("6. Extortion + sale on\nBreachForums\n(AT&T, Ticketmaster,\nSantander, ~165 orgs)", "grey"),
    ]
    for i, (t, k) in enumerate(steps):
        x = 1.1 + i * 2.15
        box(ax, x, 2.6, 1.95, 1.6, t, k, fs=7.6)
        if i:
            arrow(ax, x - 1.15, 2.6, x - 1.0, 2.6)
    ax.text(6.5, 0.9, "Root cause: customer-side identity controls (MFA, credential hygiene, network allow-lists) - "
            "no vulnerability in the Snowflake platform itself (Mandiant, 2024).",
            ha="center", fontsize=8.5, style="italic", color=C["red_e"])
    save(fig, "q2_attack_chain.png")


def q2_shared_responsibility():
    fig, ax = canvas(12, 6.2, "Figure: SaaS shared-responsibility breakdown for Snowflake - where the failure occurred")
    rows = [
        ("Data classification & governance", "Customer", True),
        ("Identity & access: users, MFA, password rotation", "Customer", True),
        ("Network policies / IP allow-lists", "Customer", True),
        ("Monitoring of login & query activity", "Customer (Snowflake provides logs)", True),
        ("Third-party / contractor endpoint security", "Customer", True),
        ("Authentication features (MFA, SSO, key-pair, PATs)", "Snowflake provides; customer enables", False),
        ("Application & database engine (SaaS)", "Snowflake", False),
        ("Encryption at rest / in transit, key management", "Snowflake (default)", False),
        ("Underlying IaaS: AWS / Azure / GCP compute & storage", "Snowflake + hyperscaler", False),
        ("Physical data centres", "Hyperscaler", False),
    ]
    ax.text(0.3, 5.75, "Layer / control", fontsize=9, fontweight="bold")
    ax.text(6.6, 5.75, "Responsible party", fontsize=9, fontweight="bold")
    ax.text(10.2, 5.75, "Failed?", fontsize=9, fontweight="bold")
    for i, (layer, who, failed) in enumerate(rows):
        y = 5.3 - i * 0.5
        kind = "red" if failed else ("amber" if "enables" in who else "green")
        ax.add_patch(FancyBboxPatch((0.2, y - 0.2), 11.6, 0.42, boxstyle="round,pad=0.01", fc=C[kind],
                                    ec=C[kind + "_e"], lw=0.8))
        ax.text(0.35, y, layer, fontsize=8.5, va="center")
        ax.text(6.6, y, who, fontsize=8.5, va="center")
        ax.text(10.35, y, "YES" if failed else "No", fontsize=8.5, va="center",
                fontweight="bold", color=C["red_e"] if failed else C["green_e"])
    ax.text(0.2, 0.15, "Red = customer responsibility that failed; amber = shared (provider supplies, customer must "
            "configure); green = provider responsibility, not implicated.", fontsize=7.8, style="italic")
    save(fig, "q2_shared_responsibility.png")


def q3_azure_architecture():
    fig, ax = canvas(13.5, 6.6, "Figure: Proposed Azure architecture for real-time ESG message triage")
    # sources
    box(ax, 1.1, 5.4, 1.8, 0.6, "Outlook / Exchange\n(email)", "grey")
    box(ax, 1.1, 4.4, 1.8, 0.6, "Service portal\n(Power Apps / web form)", "grey")
    box(ax, 1.1, 3.4, 1.8, 0.6, "Teams chat\n(Bot Service)", "grey")
    box(ax, 3.6, 4.4, 2.0, 0.9, "Logic Apps /\nPower Automate\ningest + normalise", "blue")
    box(ax, 6.0, 4.4, 2.0, 0.9, "Azure Service Bus\nqueue 'esg-inbound'\n(buffer, retry, DLQ)", "blue")
    box(ax, 8.5, 4.4, 2.3, 1.0, "Azure Functions\ntriage orchestrator\n1. AI Language PII redaction\n2. call LLM  3. validate JSON",
        "purple", fs=7.6, bold=False)
    box(ax, 8.5, 6.0, 2.3, 0.6, "Azure OpenAI (GPT-4o-mini)\nvia Azure AI Foundry", "purple")
    box(ax, 6.0, 6.0, 2.1, 0.6, "Azure AI Content Safety\nprompt shields", "purple", fs=7.5)
    box(ax, 11.4, 5.5, 2.2, 0.6, "Cosmos DB / Azure SQL\ntriage records", "green")
    box(ax, 11.4, 4.4, 2.2, 0.6, "ServiceNow / Dynamics\nticket to team", "amber")
    box(ax, 11.4, 3.3, 2.2, 0.6, "Teams / SMS alert\nCRITICAL & HIGH", "red")
    box(ax, 8.5, 2.6, 2.3, 0.8, "Human review queue\n(Power Apps)\nlow confidence, conduct,\ninjection flagged", "red", fs=7.6)
    box(ax, 11.4, 2.0, 2.2, 0.7, "Fabric / Synapse ->\nPower BI ESG dashboard", "green")
    box(ax, 5.0, 1.2, 9.4, 0.9, "Cross-cutting security & governance: Entra ID + Managed Identities (no keys in code) | Key Vault | "
        "Private Endpoints + VNet\nAzure Monitor / App Insights (latency, cost, drift) | Microsoft Purview (classification, "
        "retention) | Defender for Cloud\nAzure ML prompt flow evaluation (accuracy vs gold-labelled test set)", "grey", fs=7.5)
    for y in (5.4, 4.4, 3.4):
        arrow(ax, 2.0, y, 2.6, 4.4)
    arrow(ax, 4.6, 4.4, 5.0, 4.4)
    arrow(ax, 7.0, 4.4, 7.35, 4.4, "trigger", ly=0.25)
    arrow(ax, 8.5, 4.9, 8.5, 5.7, "redacted\nprompt", lx=0.55, style="<|-|>")
    arrow(ax, 7.35, 4.8, 6.6, 5.7, "screen", fs=6.5)
    arrow(ax, 9.65, 4.6, 10.3, 5.5)
    arrow(ax, 9.65, 4.4, 10.3, 4.4)
    arrow(ax, 9.65, 4.2, 10.3, 3.3)
    arrow(ax, 8.5, 3.9, 8.5, 3.0, "needs review", lx=0.6)
    arrow(ax, 11.4, 5.2, 11.4, 2.35, "", ls="--", color=C["green_e"], rad=-0.35)
    save(fig, "q3_azure_architecture.png")


if __name__ == "__main__":
    q1_conversation_map()
    q1_cloud_workflow()
    q2_attack_chain()
    q2_shared_responsibility()
    q3_azure_architecture()
