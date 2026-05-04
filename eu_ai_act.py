"""
EU AI Act - Regulation (EU) 2024/1689
Source: Official EU Regulation, text of 13 June 2024
Cross-referenced from authoritativeintelligenceact.eu, official EU
Commission publications, and the AI Act Service Desk.

Key dates (verified):
- Entered into force: 1 August 2024
- Prohibited practices (Article 5) and AI literacy: enforceable from 2 February 2025
- Governance rules + GPAI obligations: applicable from 2 August 2025
- Most provisions including high-risk obligations: applicable from 2 August 2026
- High-risk AI in regulated products (Annex II): applicable from 2 August 2027
- Note: Digital Omnibus proposal (Nov 2025) may adjust high-risk timeline

Penalty structure:
- Prohibited practices: up to €35M or 7% of global annual turnover
- High-risk system violations: up to €15M or 3% of global annual turnover
- Other violations: up to €7.5M or 1% of global annual turnover

The Act takes a four-tier risk-based approach:
1. Unacceptable risk (Article 5) - prohibited
2. High risk (Article 6 + Annex III) - heavily regulated
3. Limited risk (Article 50) - transparency obligations
4. Minimal risk - largely unregulated

Plus separate provisions for General-Purpose AI (GPAI) models.
"""

# =============================================================================
# Risk tier framework entries - what the agent uses for classification
# =============================================================================
EU_AI_ACT_RISK_TIERS = [
    {
        "id": "EU-TIER-1-UNACCEPTABLE",
        "title": "Unacceptable Risk - Prohibited Practices (Article 5)",
        "framework": "EU AI Act",
        "category": "Risk Tier",
        "requirement": "AI practices listed in Article 5 are prohibited. Enforceable since 2 February 2025. Non-compliance triggers fines up to EUR 35 million or 7% of global annual turnover, whichever is higher.",
        "evidence_examples": "Documented confirmation that AI system does not engage in any of the 8 prohibited practices; legal review against Article 5; documented assessment retained.",
        "common_gaps": "Practices unintentionally falling into prohibited categories (especially emotion recognition in workplace, manipulative techniques, untargeted facial scraping); no systematic Article 5 check; assumption that 'we're not law enforcement so this doesn't apply' (most prohibitions apply to all actors).",
        "details": """Article 5 prohibits 8 distinct AI practices when placed on the market, put into service, or used in the EU:

(a) Subliminal, manipulative, or deceptive techniques: AI systems deploying techniques beyond a person's consciousness, or purposefully manipulative or deceptive techniques, with the objective or effect of materially distorting behaviour, causing or reasonably likely to cause significant harm.

(b) Exploiting vulnerabilities: AI systems exploiting vulnerabilities of natural persons or specific groups due to their age, disability, or specific social or economic situation, with the objective or effect of materially distorting their behaviour and causing or likely to cause significant harm.

(c) Social scoring: AI systems for evaluation or classification of natural persons or groups based on social behaviour, personality characteristics, or known/inferred/predicted traits, with social scores leading to detrimental or unfavourable treatment in social contexts unrelated to where the data was originally generated, or unjustified/disproportionate treatment.

(d) Predictive policing based solely on profiling: AI systems making risk assessments to predict an individual's risk of committing a criminal offense based solely on profiling or assessing personality traits/characteristics. Exception: AI systems used to support human assessment based on objective and verifiable facts directly linked to criminal activity.

(e) Untargeted facial recognition database creation: AI systems that create or expand facial recognition databases through untargeted scraping of facial images from the internet or CCTV footage.

(f) Emotion recognition in workplaces and education: AI systems inferring emotions of natural persons in workplaces and educational institutions. Exception: where AI is intended to be put in place or into the market for medical or safety reasons.

(g) Biometric categorisation for sensitive attributes: AI systems categorising natural persons individually based on their biometric data to deduce or infer race, political opinions, trade union membership, religious or philosophical beliefs, sex life, or sexual orientation. Exception: lawful labelling/filtering of legally acquired biometric datasets in law enforcement.

(h) Real-time remote biometric identification in publicly accessible spaces for law enforcement: Generally prohibited. Narrow exceptions exist only for: targeted search for victims of specific crimes, prevention of specific imminent threats including terrorism, and identification of suspects of specific serious crimes (Annex II offenses). Even these exceptions require: prior judicial/administrative authorisation (with narrow urgency exception), fundamental rights impact assessment per Article 27, and registration in EU database per Article 49."""
    },
    {
        "id": "EU-TIER-2-HIGH-RISK",
        "title": "High Risk Systems (Article 6)",
        "framework": "EU AI Act",
        "category": "Risk Tier",
        "requirement": "High-risk AI systems must comply with comprehensive requirements (Articles 8-15) including risk management, data governance, technical documentation, transparency, human oversight, accuracy, robustness, and cybersecurity. Most obligations applicable from 2 August 2026 (Annex II products: 2 August 2027).",
        "evidence_examples": "Risk management system per Article 9; data governance per Article 10; technical documentation per Article 11; record-keeping/logs per Article 12; transparency information for deployers per Article 13; human oversight per Article 14; accuracy/robustness/cybersecurity per Article 15; conformity assessment; CE marking; EU database registration per Article 49; post-market monitoring; serious incident reporting.",
        "common_gaps": "System not classified despite meeting Annex III criteria; risk management ad-hoc; conformity assessment not performed; not registered in EU database; profiling auto-triggers high-risk but not recognized; Article 6(3) exception used without proper documentation.",
        "details": """An AI system is high-risk if it falls under either of two paths:

PATH 1 - Annex I products (applicable from 2 August 2027):
The AI system is a safety component of, or is itself, a product covered by Union harmonisation legislation listed in Annex I (medical devices, machinery, toys, vehicles, etc.) AND that product requires third-party conformity assessment under that legislation.

PATH 2 - Annex III standalone systems (applicable from 2 August 2026):
The AI system is listed in any of the 8 areas in Annex III (see EU-ANNEX-III entries).

ARTICLE 6(3) EXCEPTION:
An Annex III system is NOT considered high-risk if it:
- Performs a narrow procedural task, OR
- Improves the result of a previously completed human activity, OR
- Detects decision-making patterns or deviations without replacing human assessment, OR
- Performs a preparatory task to an Annex III assessment.

CRITICAL: This exception does NOT apply if the AI system performs profiling of natural persons (per GDPR Article 4(4)) — profiling auto-triggers high-risk classification.

The provider must document the assessment before placing on market and may be required to register and provide documentation to authorities.

KEY OBLIGATIONS for high-risk providers (Articles 8-15):
1. Risk management system (Article 9): continuous, iterative process throughout lifecycle
2. Data and data governance (Article 10): training/validation/testing data must be relevant, representative, free of errors to extent possible
3. Technical documentation (Article 11): drawn up before placing on market, kept current
4. Record-keeping (Article 12): automatic event logging for traceability
5. Transparency to deployers (Article 13): instructions for use enabling deployer compliance
6. Human oversight (Article 14): designed to be effectively overseen by humans
7. Accuracy, robustness, cybersecurity (Article 15): appropriate level given intended purpose

DEPLOYER obligations (Article 26): use as per instructions, ensure input data appropriateness, monitor operation, retain logs, inform individuals subject to AI decisions, fundamental rights impact assessment for certain deployers (Article 27).

PENALTIES: Up to EUR 15 million or 3% of global annual turnover for high-risk violations."""
    },
    {
        "id": "EU-TIER-3-LIMITED-RISK",
        "title": "Limited Risk - Transparency Obligations (Article 50)",
        "framework": "EU AI Act",
        "category": "Risk Tier",
        "requirement": "AI systems with specific transparency risks must meet disclosure obligations under Article 50. Applicable from 2 August 2026.",
        "evidence_examples": "User notifications confirming interaction with AI; deepfake labelling mechanisms; emotion recognition disclosures; AI-generated public-interest text disclosures; machine-readable marking of synthetic content.",
        "common_gaps": "Users not informed they're interacting with chatbot; AI-generated content not labelled; deepfakes published without disclosure; no machine-readable watermarking on synthetic content.",
        "details": """Article 50 imposes specific transparency obligations:

PROVIDER obligations:
- AI systems intended to interact with natural persons (chatbots): users must be informed they are interacting with AI, unless this is obvious from context to a reasonably well-informed person
- AI systems generating synthetic audio, image, video, or text content: outputs must be marked in machine-readable format and detectable as artificially generated/manipulated

DEPLOYER obligations:
- Emotion recognition systems and biometric categorisation systems: persons exposed to such systems must be informed (subject to law enforcement exceptions)
- AI systems generating or manipulating image/audio/video constituting deepfakes: must disclose that content is artificially generated (with exceptions for clearly artistic/creative/satirical works, where disclosure should not hamper enjoyment)
- AI systems generating or manipulating text published to inform public on matters of public interest: disclose AI-generated unless human-reviewed and editorial responsibility taken

Limited risk systems do NOT need to meet the comprehensive Chapter III requirements applicable to high-risk systems."""
    },
    {
        "id": "EU-TIER-4-MINIMAL-RISK",
        "title": "Minimal Risk Systems",
        "framework": "EU AI Act",
        "category": "Risk Tier",
        "requirement": "AI systems not falling into other tiers face no specific AI Act obligations. Voluntary codes of conduct (Article 95) are encouraged.",
        "evidence_examples": "Documented risk classification rationale; voluntary adherence to codes of conduct; monitoring for scope creep that could change classification.",
        "common_gaps": "Risk classification not documented; if scope creeps into high-risk use, no reclassification; assumption that current minimal-risk status is permanent.",
        "details": """Minimal risk includes the majority of AI systems not falling into prohibited, high-risk, or limited-risk categories:
- AI-enabled video games
- Spam filters
- Inventory management systems
- Most general-purpose AI applications without high-risk use

The AI Act encourages voluntary codes of conduct (Article 95) for these systems, drawing on high-risk requirements where appropriate. Note: classification can change as use cases evolve. A system originally minimal-risk that gets repurposed for high-risk applications must be reclassified."""
    },
    {
        "id": "EU-GPAI-STANDARD",
        "title": "General-Purpose AI Models - Standard Obligations (Article 53)",
        "framework": "EU AI Act",
        "category": "GPAI Provisions",
        "requirement": "All providers of general-purpose AI models must meet transparency, documentation, copyright, and downstream-information obligations. Applicable from 2 August 2025.",
        "evidence_examples": "Technical documentation per Annex XI; instructions/information for downstream providers per Annex XII; documented copyright compliance policy; published summary of training content (using Commission template); EU representative designated where applicable.",
        "common_gaps": "GPAI obligations confused with deployer obligations; technical documentation incomplete; copyright policy absent or generic; training data summary not published; no EU representative for non-EU providers.",
        "details": """Article 53 obligations for ALL GPAI providers (excluding limited open-source exemption):

1. Maintain technical documentation including training and testing process and evaluation results (Annex XI)
2. Make information and documentation available to downstream providers integrating the model (Annex XII)
3. Put in place a policy to comply with EU copyright law, including respecting opt-outs from text and data mining (Article 4(3) of Directive (EU) 2019/790)
4. Make publicly available a sufficiently detailed summary of content used for training, using a template provided by the AI Office

OPEN-SOURCE EXEMPTION (Article 53(2)): GPAI models released under free and open-source licenses, with publicly available parameters/architecture/usage information, are exempt from obligations 1 and 2 above. They remain subject to obligations 3 (copyright) and 4 (training data summary). Note: the exemption does NOT apply if the model is classified as having systemic risk.

WHO IS A "PROVIDER" vs "DEPLOYER":
- Provider: develops the GPAI model and places it on the market
- Most enterprises using GPT-4, Claude, Gemini etc. are DEPLOYERS, not providers
- Deployers' obligations come from the high-risk/limited-risk classification of the system they BUILD using GPAI, not from these GPAI provisions"""
    },
    {
        "id": "EU-GPAI-SYSTEMIC",
        "title": "GPAI with Systemic Risk - Additional Obligations (Article 55)",
        "framework": "EU AI Act",
        "category": "GPAI Provisions",
        "requirement": "GPAI models classified as having systemic risk must meet additional obligations on top of standard GPAI requirements.",
        "evidence_examples": "Model evaluations with adversarial testing; serious incident tracking and reporting to AI Office; cybersecurity protections at frontier-scale; documented assessment and mitigation of systemic risks.",
        "common_gaps": "Systemic-risk threshold not assessed; adversarial testing absent or limited to standard prompts; serious incidents not reported to AI Office; cybersecurity not commensurate with model capabilities.",
        "details": """A GPAI model is classified as having systemic risk if either:
1. It has high-impact capabilities evaluated based on technical tools and methodologies, OR
2. The Commission decides ex officio or via qualified alert that it has equivalent capabilities

PRESUMPTION THRESHOLD: A model is presumed to have high-impact capabilities if cumulative compute used for training exceeds 10^25 FLOPs. Providers must notify the Commission within 2 weeks of meeting/expecting to meet this threshold.

ADDITIONAL OBLIGATIONS (Article 55) on top of Article 53:
1. Perform model evaluation per state-of-the-art protocols, including adversarial testing
2. Assess and mitigate possible systemic risks at Union level
3. Track, document, and report serious incidents (and possible corrective measures) to AI Office and national authorities without undue delay
4. Ensure adequate cybersecurity protection for model and physical infrastructure

Voluntary codes of practice (Article 56) can demonstrate compliance until harmonised standards exist."""
    },
]

# =============================================================================
# Annex III - The 8 high-risk areas (Article 6(2))
# =============================================================================
EU_AI_ACT_ANNEX_III = [
    {
        "id": "ANNEX-III-1-BIOMETRICS",
        "title": "Annex III(1) - Biometrics",
        "framework": "EU AI Act",
        "category": "Annex III High-Risk Areas",
        "requirement": "AI systems in biometrics that are not prohibited under Article 5 are high-risk under Annex III(1).",
        "evidence_examples": "Annex III high-risk classification documented; conformity assessment with notified body involvement (required for biometrics); EU database registration; impact assessment.",
        "common_gaps": "Confusion between prohibited Article 5 biometric uses and high-risk Annex III biometrics; biometric verification mistakenly classified as high-risk (it's not); failure to involve notified body in conformity assessment.",
        "details": """High-risk biometric systems include:

(a) Remote biometric identification systems (NOT including biometric verification for confirming a person's claimed identity)
(b) Biometric categorisation according to sensitive or protected attributes (where not already prohibited under Article 5)
(c) Emotion recognition systems (where not already prohibited under Article 5 in workplaces/education)

Important distinction: Biometric verification (e.g., fingerprint to unlock your phone, face match for boarding) is NOT high-risk. Remote biometric identification (one-to-many search) IS high-risk.

Real-time remote biometric identification in publicly accessible spaces for law enforcement falls under Article 5 (prohibited with narrow exceptions), not high-risk Annex III.

NOTE: Biometric systems require conformity assessment by a notified body (third-party assessment), unlike most other Annex III categories where internal assessment suffices."""
    },
    {
        "id": "ANNEX-III-2-CRITICAL-INFRA",
        "title": "Annex III(2) - Critical Infrastructure",
        "framework": "EU AI Act",
        "category": "Annex III High-Risk Areas",
        "requirement": "AI systems used as safety components in management/operation of critical infrastructure are high-risk under Annex III(2).",
        "evidence_examples": "Documented role as safety component; integration with sector-specific safety regulations; conformity assessment; redundancy and resilience controls.",
        "common_gaps": "AI used in critical infrastructure but not classified as 'safety component'; sector-specific safety requirements not integrated with AI Act obligations.",
        "details": """Covers AI systems intended to be used as safety components in:
- Management and operation of critical digital infrastructure
- Road traffic
- Supply of water, gas, heating, electricity

Note: Only AI used as 'safety components' (failure could endanger life/health) qualifies. AI for purely operational efficiency without safety implications may not be high-risk."""
    },
    {
        "id": "ANNEX-III-3-EDUCATION",
        "title": "Annex III(3) - Education and Vocational Training",
        "framework": "EU AI Act",
        "category": "Annex III High-Risk Areas",
        "requirement": "AI systems determining access, evaluating learning outcomes, or detecting prohibited test behaviour in education are high-risk.",
        "evidence_examples": "High-risk classification for admission/scoring systems; bias testing across student demographics; appeal mechanisms for AI-influenced decisions; transparent communication to students.",
        "common_gaps": "AI used in admissions or grading not classified as high-risk; bias not tested; students unaware of AI involvement in decisions affecting them.",
        "details": """High-risk AI systems in education include those used to:
(a) Determine access, admission, or assignment to educational and vocational training institutions at all levels
(b) Evaluate learning outcomes, including those used to steer student learning
(c) Assess the appropriate level of education an individual will receive or be able to access
(d) Monitor and detect prohibited behaviour of students during tests

Common applications: AI for admissions, AI grading systems, AI-driven adaptive learning that tracks individuals, AI proctoring."""
    },
    {
        "id": "ANNEX-III-4-EMPLOYMENT",
        "title": "Annex III(4) - Employment, Workers Management, Self-Employment Access",
        "framework": "EU AI Act",
        "category": "Annex III High-Risk Areas",
        "requirement": "AI systems used in recruitment, work allocation, evaluation, or termination decisions are high-risk.",
        "evidence_examples": "High-risk classification documented for HR AI; bias testing across protected attributes; human oversight in hiring decisions; informed consent of candidates; integration with employment law (national); fundamental rights impact assessment.",
        "common_gaps": "Resume screening AI not recognized as high-risk; performance monitoring AI deployed without oversight; gig work allocation AI used without bias testing; emotion recognition in workplace (note: this is PROHIBITED under Article 5, not high-risk).",
        "details": """High-risk AI systems in employment include those used for:
(a) Recruitment and selection (placing job advertisements, analysing/filtering applications, evaluating candidates)
(b) Decisions affecting terms of work-related relationships (promotion, termination)
(c) Allocating tasks based on individual behaviour or personal traits
(d) Monitoring and evaluating performance and behaviour

Common applications: ATS (applicant tracking systems) with AI scoring, AI-driven performance management, gig economy task allocation algorithms, AI-driven termination recommendation systems.

IMPORTANT: Emotion recognition in the workplace is PROHIBITED under Article 5(1)(f), not merely high-risk."""
    },
    {
        "id": "ANNEX-III-5-ESSENTIAL-SERVICES",
        "title": "Annex III(5) - Essential Private and Public Services",
        "framework": "EU AI Act",
        "category": "Annex III High-Risk Areas",
        "requirement": "AI systems determining access to essential services including credit, insurance, public benefits, and emergency dispatching are high-risk.",
        "evidence_examples": "High-risk classification for credit scoring/insurance underwriting; bias testing; explainability of decisions; appeal mechanisms; documentation of training data representativeness.",
        "common_gaps": "Credit scoring AI not classified as high-risk; insurance pricing AI without fairness testing; benefits eligibility AI without appeal mechanism; healthcare triage AI without clinician oversight.",
        "details": """High-risk AI systems in essential services include those used for:
(a) Evaluating eligibility for public benefits and services (including healthcare)
(b) Credit scoring or assessing creditworthiness (EXCEPTION: AI used for detecting financial fraud is NOT in Annex III)
(c) Risk assessment and pricing for life and health insurance
(d) Dispatching or establishing priority in emergency services (police, fire, medical, urgent triage)

Common applications: Credit scoring algorithms, insurance underwriting AI, welfare/benefits eligibility systems, emergency call triage AI."""
    },
    {
        "id": "ANNEX-III-6-LAW-ENFORCEMENT",
        "title": "Annex III(6) - Law Enforcement",
        "framework": "EU AI Act",
        "category": "Annex III High-Risk Areas",
        "requirement": "AI systems used by law enforcement for risk assessment, polygraph, evidence reliability, or crime profiling are high-risk (unless prohibited under Article 5).",
        "evidence_examples": "High-risk classification; integration with criminal procedural safeguards; human oversight; documented evidence reliability assessment; conformity assessment.",
        "common_gaps": "Predictive policing tools not properly classified; AI evidence analysis without reliability assessment; profiling tools without proper safeguards; intersection with prohibited Article 5 practices unclear.",
        "details": """High-risk AI systems in law enforcement (insofar as their use is permitted under EU/national law) include those used:
(a) To assess the risk of a natural person becoming a victim of criminal offences
(b) As polygraphs and similar tools
(c) To evaluate the reliability of evidence in criminal investigations or prosecutions
(d) For assessing the risk of an individual offending or re-offending NOT solely based on profiling, or to assess personality traits or past criminal behaviour
(e) For profiling natural persons in the course of detection, investigation, or prosecution of criminal offences

NOTE: Predictive policing based SOLELY on profiling is PROHIBITED under Article 5(1)(d). The high-risk category covers law enforcement AI that supports human assessment with broader inputs."""
    },
    {
        "id": "ANNEX-III-7-MIGRATION",
        "title": "Annex III(7) - Migration, Asylum, and Border Control",
        "framework": "EU AI Act",
        "category": "Annex III High-Risk Areas",
        "requirement": "AI systems used in migration, asylum, and border control management are high-risk.",
        "evidence_examples": "High-risk classification; integration with refugee protection law; bias testing across nationalities; human oversight of decisions affecting fundamental rights; appeal mechanisms.",
        "common_gaps": "Visa decision AI not classified as high-risk; asylum risk assessment AI without proper safeguards; border surveillance AI without rights impact assessment.",
        "details": """High-risk AI systems in migration include those used:
(a) As polygraphs or similar tools
(b) To assess risk including security, irregular migration, or health risks of natural persons entering EU territory
(c) To assist in examining applications for asylum, visa, residence permits, and related complaints regarding eligibility
(d) For detecting, recognising, or identifying natural persons in migration/asylum/border contexts (EXCEPT verification of travel documents)

Note: This is one of the categories where intersection with EU fundamental rights is most acute."""
    },
    {
        "id": "ANNEX-III-8-JUSTICE-DEMOCRACY",
        "title": "Annex III(8) - Administration of Justice and Democratic Processes",
        "framework": "EU AI Act",
        "category": "Annex III High-Risk Areas",
        "requirement": "AI systems assisting judicial authorities or influencing elections are high-risk.",
        "evidence_examples": "High-risk classification; preserving judicial independence; transparency of AI involvement in judicial decisions; election integrity protections.",
        "common_gaps": "AI assistance to judges not properly classified; AI-driven political microtargeting risks not assessed; chilling effects on democratic participation overlooked.",
        "details": """High-risk AI systems in justice and democracy include those used:
(a) By judicial authorities (or on their behalf) to assist in researching/interpreting facts and law, and applying law to concrete facts
(b) For dispute resolution
(c) To influence the outcome of elections or referenda or the voting behaviour of natural persons (EXCEPTION: AI tools used purely for administration/organisation of campaigns and not directly engaging with voters)

Common applications: Judicial decision support systems, AI legal research tools used by courts, political microtargeting algorithms."""
    },
]