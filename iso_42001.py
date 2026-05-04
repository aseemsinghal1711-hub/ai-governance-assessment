"""
ISO/IEC 42001:2023 - AI Management System
All 38 Annex A controls organized into 9 groups.

Source: Cross-referenced from authoritative public guidance, primarily
PECB-certified ISO 42001 training materials (orbit.reconn.io, ISMS.online,
Hicomply, Glocert International). The control IDs and titles match the
official standard structure.

For production KPMG use, replace the requirement and evidence_examples 
fields with content from the licensed ISO 42001 standard. The IDs and 
structure here are the authoritative ones.
"""

ISO_42001_CONTROLS = [
    # =========================================================================
    # A.2 - Policies for AI (3 controls)
    # =========================================================================
    {
        "id": "A.2.2",
        "title": "AI policy",
        "framework": "ISO 42001",
        "category": "A.2 Policies for AI",
        "requirement": "The organization shall document a policy for the development or use of AI systems, informed by business strategy, organizational values, level of risk posed by AI systems, legal requirements, and the risk environment.",
        "evidence_examples": "Approved AI policy document; communicated to relevant personnel; reviewed periodically; signed by leadership; processes for handling policy exceptions documented.",
        "common_gaps": "Generic IT policy used as substitute; no specific AI provisions; not communicated; outdated; no review cadence; policy describes intent without shaping behaviour."
    },
    {
        "id": "A.2.3",
        "title": "Alignment with other organizational policies",
        "framework": "ISO 42001",
        "category": "A.2 Policies for AI",
        "requirement": "The organization shall determine where other organizational policies (quality, security, privacy, safety, ethics) can apply to or be affected by AI and align accordingly.",
        "evidence_examples": "Mapping of AI policy to existing privacy, security, ethics, and HR policies; documented alignment review; updated existing policies to incorporate AI-specific provisions.",
        "common_gaps": "AI policy created in isolation from existing privacy and security policies; conflicts not identified; no analysis of intersection points."
    },
    {
        "id": "A.2.4",
        "title": "Review of the AI policy",
        "framework": "ISO 42001",
        "category": "A.2 Policies for AI",
        "requirement": "The AI policy shall be reviewed at planned intervals or when significant changes occur, with a named management-approved role owning the review.",
        "evidence_examples": "Documented review cycle; minutes of review meetings; updates triggered by regulation changes; named accountable role; review records retained.",
        "common_gaps": "No review schedule; policy stale; trigger conditions undefined; review not driven by environmental changes."
    },

    # =========================================================================
    # A.3 - Internal Organisation (2 controls)
    # =========================================================================
    {
        "id": "A.3.2",
        "title": "AI roles and responsibilities",
        "framework": "ISO 42001",
        "category": "A.3 Internal Organisation",
        "requirement": "Roles and responsibilities for AI shall be defined, allocated, and communicated, with explicit accountability for AI risk, output review, escalation, and authority to halt AI processes.",
        "evidence_examples": "RACI matrix for AI; defined accountability for AI risk owner, model owner, data steward; org chart showing AI governance roles; documented authority to halt AI processes.",
        "common_gaps": "Unclear ownership; no AI risk officer; data scientists held responsible for governance they aren't equipped to handle; structure on paper differs from actual decision-making authority."
    },
    {
        "id": "A.3.3",
        "title": "Reporting of concerns",
        "framework": "ISO 42001",
        "category": "A.3 Internal Organisation",
        "requirement": "A formal mechanism shall exist for personnel to raise concerns about AI behaviour, outputs, or associated risks without fear of retaliation.",
        "evidence_examples": "Whistleblower channel covering AI concerns; ethics hotline; documented escalation paths; staff awareness of mechanism; psychological safety verified through interviews.",
        "common_gaps": "Mechanism exists in policy but staff are unaware of it or don't trust it; no specific channel for AI ethics concerns; relies on general grievance process."
    },

    # =========================================================================
    # A.4 - Resources for AI Systems (6 controls)
    # =========================================================================
    {
        "id": "A.4.1",
        "title": "AI system inventory",
        "framework": "ISO 42001",
        "category": "A.4 Resources for AI Systems",
        "requirement": "The organization shall maintain an inventory of AI systems within the AIMS scope, kept current as systems are deployed, modified, or decommissioned.",
        "evidence_examples": "Maintained AI system inventory with system names, owners, purpose, lifecycle state; documented update process; coverage check during audits.",
        "common_gaps": "No central inventory; shadow AI not tracked; inventory outdated; scope unclear because inventory absent; impact assessment running without inventory completion."
    },
    {
        "id": "A.4.2",
        "title": "Resource documentation",
        "framework": "ISO 42001",
        "category": "A.4 Resources for AI Systems",
        "requirement": "The organization shall document the resources used by each AI system, including components, data, tooling, computing infrastructure, and human expertise.",
        "evidence_examples": "AI system documentation listing compute infrastructure, training data sources, tools used, team members and roles; cross-referenced with risk assessment.",
        "common_gaps": "Resources scattered across team knowledge; no central documentation; resources required not actually verified as available."
    },
    {
        "id": "A.4.3",
        "title": "Data resources",
        "framework": "ISO 42001",
        "category": "A.4 Resources for AI Systems",
        "requirement": "Data used or to be used by the AI system shall be documented including provenance, last-updated dates, categories, labelling processes, intended use, quality, retention policies, known bias issues, and preparation steps.",
        "evidence_examples": "Data sheets/cards for each dataset; documented provenance; labelling process documentation; quality metrics; consent and licensing records; bias assessment results.",
        "common_gaps": "Training data provenance undocumented; bias assessment absent; quality assessed informally; limited visibility into where training data came from."
    },
    {
        "id": "A.4.4",
        "title": "Tooling resources",
        "framework": "ISO 42001",
        "category": "A.4 Resources for AI Systems",
        "requirement": "Tools used to develop, deploy, and operate AI systems shall be documented, including algorithmic types, ML models, data conditioning tools, evaluation methods, and development/deployment tooling.",
        "evidence_examples": "Inventory of ML platforms, model registries, experiment tracking tools, deployment pipelines; documented appropriateness of tools for intended applications.",
        "common_gaps": "Shadow AI tools used by individual teams; no central tracking; security review of tools missing; tooling appropriateness not assessed."
    },
    {
        "id": "A.4.5",
        "title": "System and computing resources",
        "framework": "ISO 42001",
        "category": "A.4 Resources for AI Systems",
        "requirement": "System and computing resources used in the AI lifecycle shall be documented, including hardware, hosting environment, processing, storage, and environmental impact.",
        "evidence_examples": "Documented compute infrastructure; cloud account inventory; GPU usage tracking; environmental impact disclosure; energy consumption tracking.",
        "common_gaps": "Compute usage not tracked; no environmental impact assessment; cost attribution unclear; energy consumption of training/inference not measured."
    },
    {
        "id": "A.4.6",
        "title": "Human resources",
        "framework": "ISO 42001",
        "category": "A.4 Resources for AI Systems",
        "requirement": "Human resources involved in the AI system lifecycle shall be documented including their competencies, with attention to diverse expertise where datasets affect particular communities.",
        "evidence_examples": "Skills matrix; training records; certifications; documented role assignments per AI system; demographic representation considered for relevant systems.",
        "common_gaps": "No skills inventory; team competencies assumed; training not tracked; lack of diverse expertise on teams working with sensitive data."
    },

    # =========================================================================
    # A.5 - Assessing Impacts of AI Systems (3 controls)
    # =========================================================================
    {
        "id": "A.5.2",
        "title": "AI system impact assessment process",
        "framework": "ISO 42001",
        "category": "A.5 Assessing Impacts of AI Systems",
        "requirement": "The organization shall establish and maintain a repeatable, documented process to assess potential impacts of AI systems on individuals, groups, and society.",
        "evidence_examples": "Documented AI impact assessment methodology; templates; trigger criteria; review board; capability to apply consistently across different AI systems with different risk profiles.",
        "common_gaps": "No formal impact assessment methodology; only privacy DPIA exists; ethics not considered systematically; methodology exists but not consistently applied."
    },
    {
        "id": "A.5.3",
        "title": "Internal impact assessment of AI systems",
        "framework": "ISO 42001",
        "category": "A.5 Assessing Impacts of AI Systems",
        "requirement": "Each AI system within scope shall be assessed using the impact assessment process, examining discriminatory outcomes, privacy violations, safety risks, and broader societal effects, feeding into deployment decisions.",
        "evidence_examples": "Completed AI impact assessments for each in-scope system; sign-offs; mitigation plans; controls aligned with assessment findings; updates when systems change.",
        "common_gaps": "Process documented but no evidence assessments were actually conducted; impact assessments missing for legacy systems; assessments not updated when systems change; high-impact systems deployed without adequate controls."
    },
    {
        "id": "A.5.4",
        "title": "Functionality and behaviour of the AI system",
        "framework": "ISO 42001",
        "category": "A.5 Assessing Impacts of AI Systems",
        "requirement": "Controls shall ensure AI systems function as intended and that deviations from expected behaviour are detected and addressed.",
        "evidence_examples": "Behavioural monitoring against impact assessments; deviation detection mechanisms; documented response procedures when behaviour deviates from expectations.",
        "common_gaps": "No behavioural monitoring after deployment; deviations only discovered after user complaints; no link between operational monitoring and original impact assessment."
    },

    # =========================================================================
    # A.6 - AI System Life Cycle (10 controls)
    # =========================================================================
    {
        "id": "A.6.1.1",
        "title": "Design of the AI system",
        "framework": "ISO 42001",
        "category": "A.6 AI System Life Cycle",
        "requirement": "Requirements and design specifications shall be documented before development begins, reflecting intended use case, identified risks, and governance constraints from the AI policy.",
        "evidence_examples": "Documented design specifications; architecture diagrams; design decisions log; traceability from requirements to design choices.",
        "common_gaps": "Design documented in scattered notebooks; design decisions not traceable; no link between design and AI policy constraints."
    },
    {
        "id": "A.6.1.2",
        "title": "Data for development and enhancement",
        "framework": "ISO 42001",
        "category": "A.6 AI System Life Cycle",
        "requirement": "Data used in AI system development shall be governed for privacy/security implications, security/safety threats from data-dependent development, transparency and explainability, representativeness, and accuracy/integrity.",
        "evidence_examples": "Data governance documentation specific to development; representativeness analysis; data accuracy verification; data integrity controls in pipelines.",
        "common_gaps": "Data sourcing without legal review; representativeness assumed; no integrity controls; development data privacy not assessed."
    },
    {
        "id": "A.6.1.3",
        "title": "AI system development documentation",
        "framework": "ISO 42001",
        "category": "A.6 AI System Life Cycle",
        "requirement": "Documentation maintained throughout development capturing design decisions, testing procedures, validation results, and changes — creating an audit trail showing the system was built according to specifications and governance requirements.",
        "evidence_examples": "Living development documentation; model cards; design decision logs; testing procedure documentation; change history.",
        "common_gaps": "Documentation lags behind development; tribal knowledge required to operate; key decisions not traceable; documentation describes a different system than what was actually built."
    },
    {
        "id": "A.6.1.4",
        "title": "Addressing bias in data",
        "framework": "ISO 42001",
        "category": "A.6 AI System Life Cycle",
        "requirement": "Explicit controls for identifying, assessing, and addressing bias in training and operational data shall be implemented.",
        "evidence_examples": "Documented bias assessment methodology; bias testing across protected attributes; bias mitigation actions; expertise on team or external reviewers.",
        "common_gaps": "No bias assessment methodology defined; general awareness mistaken for a control; bias assessment limited to one or two attributes; no mitigation actions when bias is found."
    },
    {
        "id": "A.6.1.5",
        "title": "Robustness of AI systems",
        "framework": "ISO 42001",
        "category": "A.6 AI System Life Cycle",
        "requirement": "AI systems shall maintain intended performance under adversarial conditions, edge cases, and unexpected inputs.",
        "evidence_examples": "Robustness testing methodology; adversarial testing results; edge case analysis; documented response to inputs designed to elicit incorrect behaviour.",
        "common_gaps": "Standard functional testing only; adversarial testing absent; edge cases discovered in production; no AI-specific attack testing."
    },
    {
        "id": "A.6.2.1",
        "title": "AI system operational concept",
        "framework": "ISO 42001",
        "category": "A.6 AI System Life Cycle",
        "requirement": "Documentation of how the AI system is intended to operate in its deployment environment, including users, use cases, interfaces, and operational constraints.",
        "evidence_examples": "Operational concept document; defined users and use cases; documented operational constraints; basis for what 'correct operation' looks like in monitoring.",
        "common_gaps": "Operational concept implicit; users and use cases drift from intent; monitoring has no baseline to measure against."
    },
    {
        "id": "A.6.2.2",
        "title": "AI system testing",
        "framework": "ISO 42001",
        "category": "A.6 AI System Life Cycle",
        "requirement": "Structured testing before deployment shall verify that the system performs as specified, with documented scope, methodology, test data, results, and sign-off.",
        "evidence_examples": "Test plans; documented methodology; preserved test sets; validation reports; performance metrics on holdout data; fairness testing results; sign-off records.",
        "common_gaps": "Tests run informally; test sets not preserved; testing scope inadequate relative to risk profile; sign-off pro forma; deployment driven by deadlines."
    },
    {
        "id": "A.6.2.3",
        "title": "Human oversight of AI systems",
        "framework": "ISO 42001",
        "category": "A.6 AI System Life Cycle",
        "requirement": "Reviewers with genuine authority to override AI decisions shall be in place; AI output accuracy and consistency shall be monitored; mechanisms shall exist for personnel to report concerns; appropriateness of automated decision-making shall be assessed for each use case.",
        "evidence_examples": "Defined human-in-the-loop or human-on-the-loop model; documented authority to override; monitoring of output accuracy; reviewer training; assessment of automation appropriateness per use case.",
        "common_gaps": "Reviewers have no authority to override; oversight is nominal/rubber-stamp; monitoring of output quality absent; automation applied without appropriateness assessment."
    },
    {
        "id": "A.6.2.4",
        "title": "AI system event logs",
        "framework": "ISO 42001",
        "category": "A.6 AI System Life Cycle",
        "requirement": "AI system use shall be logged including time, date, production data processed, and outputs falling outside intended operational ranges; logs retained per system intended use and applicable legal requirements.",
        "evidence_examples": "Logged inputs/outputs (where appropriate); decision logs; user feedback logs; system event logs; retention policy aligned with legal requirements.",
        "common_gaps": "Logs missing for AI decisions; logs deleted too quickly; no correlation between logs and decisions; biometric system logging insufficient for jurisdictional requirements."
    },
    {
        "id": "A.6.2.5",
        "title": "AI system deployment",
        "framework": "ISO 42001",
        "category": "A.6 AI System Life Cycle",
        "requirement": "A documented deployment plan shall be in place with verification that all necessary requirements are met before the system goes live (a gate control covering design specifications, testing results, impact assessments, oversight mechanisms, and operational documentation).",
        "evidence_examples": "Documented deployment procedure; deployment checklist; rollback plan; staged rollout; formal gate review confirming all prerequisites met.",
        "common_gaps": "Systems deployed without completing impact assessment or testing sign-off; ad-hoc deployment; no rollback plan; production parity with development not verified."
    },

    # =========================================================================
    # A.7 - Data for AI Systems (4 controls)
    # =========================================================================
    {
        "id": "A.7.2",
        "title": "Data for development and enhancement of AI system (operational)",
        "framework": "ISO 42001",
        "category": "A.7 Data for AI Systems",
        "requirement": "Operational data management covering privacy and security in data use, security threats from data-dependent AI, transparency and explainability, representativeness of training vs operational domain, and data accuracy and integrity.",
        "evidence_examples": "Operational data governance documentation; representativeness gap monitoring; quality controls; data versioning; access controls.",
        "common_gaps": "Operational data drifts from training data; no monitoring for representativeness gap; quality assumed; access not controlled."
    },
    {
        "id": "A.7.3",
        "title": "Acquisition of data",
        "framework": "ISO 42001",
        "category": "A.7 Data for AI Systems",
        "requirement": "Data acquisition for AI systems shall be governed including categories required, quantities, sources, source characteristics, data subject demographics, prior handling, data rights (PII, copyright), labelling metadata, and provenance.",
        "evidence_examples": "Data licensing agreements; consent records; legal review of data sources; sourcing policy; data rights documentation; labelling provenance.",
        "common_gaps": "Web-scraped data used without license review; consent provenance unclear; terms of service violations; no documented sourcing process."
    },
    {
        "id": "A.7.4",
        "title": "Quality of data for AI systems",
        "framework": "ISO 42001",
        "category": "A.7 Data for AI Systems",
        "requirement": "Data quality requirements shall be defined and assessed including accuracy, completeness, consistency, and timeliness, with processes to detect and remediate quality issues.",
        "evidence_examples": "Data quality metrics; data profiling reports; quality gates in pipeline; remediation procedures; ongoing quality monitoring.",
        "common_gaps": "Quality assessed informally; no metrics; data quality issues only found after model fails in production; no remediation process."
    },
    {
        "id": "A.7.5",
        "title": "Processing of personal information",
        "framework": "ISO 42001",
        "category": "A.7 Data for AI Systems",
        "requirement": "Controls shall govern appropriate handling of personal data within AI systems, integrated with applicable privacy frameworks (GDPR, PDPA, etc.).",
        "evidence_examples": "DPIAs for AI systems processing personal data; privacy controls integrated with AI controls; documented integration with privacy framework; data subject rights handling for AI contexts.",
        "common_gaps": "Generic DPIA used; AI-specific privacy attacks not considered; data subject rights (access, deletion) unclear for AI training data; integration with privacy framework absent."
    },

    # =========================================================================
    # A.8 - Information for Interested Parties (5 controls)
    # =========================================================================
    {
        "id": "A.8.2",
        "title": "Characteristics of AI systems",
        "framework": "ISO 42001",
        "category": "A.8 Information for Interested Parties",
        "requirement": "The organization shall make information about the AI system's characteristics available to relevant interested parties, including intended use, capabilities, limitations, and conditions under which it should not be used.",
        "evidence_examples": "User-facing documentation; model cards; capability descriptions; published limitations; out-of-scope conditions documented.",
        "common_gaps": "Capabilities oversold; limitations not disclosed; users don't know they're interacting with AI; published model cards absent."
    },
    {
        "id": "A.8.3",
        "title": "AI system disclosure",
        "framework": "ISO 42001",
        "category": "A.8 Information for Interested Parties",
        "requirement": "Appropriate disclosure shall occur when individuals are interacting with or subject to decisions from an AI system, with form context-dependent (some jurisdictions like EU AI Act mandate explicit disclosure).",
        "evidence_examples": "Documented disclosure approach; user notifications when interacting with AI; deepfake labelling; jurisdictional compliance for explicit disclosure mandates.",
        "common_gaps": "Users not informed of AI interaction; AI-generated content not labelled; deepfake disclosures missing; no disclosure where no legal mandate exists."
    },
    {
        "id": "A.8.4",
        "title": "Communication of limitations",
        "framework": "ISO 42001",
        "category": "A.8 Information for Interested Parties",
        "requirement": "Users and affected parties shall be informed of the system's known limitations including conditions where accuracy degrades, edge cases where the system should not be relied upon, and known biases.",
        "evidence_examples": "Published limitation documentation; user training on system limitations; documented edge cases; bias disclosures.",
        "common_gaps": "Limitations not communicated; users assume system reliability; bias known internally but not disclosed; limitations buried in fine print."
    },
    {
        "id": "A.8.5",
        "title": "Communication of intended use",
        "framework": "ISO 42001",
        "category": "A.8 Information for Interested Parties",
        "requirement": "Clear communication of what the system was designed to do and what it was not designed to do, supporting accountability for catching and preventing out-of-scope use.",
        "evidence_examples": "Documented intended use; published out-of-scope uses; user training on appropriate use; warnings for out-of-scope queries.",
        "common_gaps": "Intended use vague; scope creep into unintended uses; users unclear on boundaries; no warnings for out-of-scope use."
    },
    {
        "id": "A.8.6",
        "title": "Communication of changes",
        "framework": "ISO 42001",
        "category": "A.8 Information for Interested Parties",
        "requirement": "Processes shall exist for communicating material changes to AI systems to affected parties — when systems are updated, retrained, or intended use is modified.",
        "evidence_examples": "Change communication procedure; stakeholder notification log; version history accessible to users; particularly important for AI deployed on behalf of clients.",
        "common_gaps": "Material changes silently deployed; users unaware of updated system behaviour; retraining not communicated; no notification process for third-party-deployed AI."
    },

    # =========================================================================
    # A.9 - Responsible Use of AI Systems (3 controls)
    # =========================================================================
    {
        "id": "A.9.2",
        "title": "Intended use of AI systems",
        "framework": "ISO 42001",
        "category": "A.9 Responsible Use of AI Systems",
        "requirement": "Controls shall ensure AI systems are used only for their intended purposes, including operational safeguards, user training, and monitoring mechanisms to detect out-of-scope use.",
        "evidence_examples": "Operational safeguards preventing out-of-scope use; user training; monitoring for misuse patterns; technical guardrails.",
        "common_gaps": "No AI-specific acceptable use policy; users improvise; out-of-scope use not detected; no technical guardrails."
    },
    {
        "id": "A.9.3",
        "title": "Responsibilities and obligations for appropriate use",
        "framework": "ISO 42001",
        "category": "A.9 Responsible Use of AI Systems",
        "requirement": "Clear documentation of responsibilities — within the organization and with external users/clients — for ensuring appropriate use, including contractual terms, user agreements, and internal accountability structures.",
        "evidence_examples": "Contractual AI use terms with clients; user agreements; internal accountability documented; training on responsibilities; obligations clearly allocated.",
        "common_gaps": "Responsibilities ambiguous; user agreements predate AI; client contracts don't address AI use; internal accountability gaps."
    },
    {
        "id": "A.9.4",
        "title": "Addressing misuse of AI systems",
        "framework": "ISO 42001",
        "category": "A.9 Responsible Use of AI Systems",
        "requirement": "The organization shall have mechanisms to detect, respond to, and learn from instances of AI misuse — by internal actors, external users, or adversarial third parties.",
        "evidence_examples": "Misuse detection mechanisms; incident response procedures for AI misuse; lessons learned process; connection to event logs (A.6.2.4) and incident management (Clause 10).",
        "common_gaps": "Misuse undetected; no specific procedures for AI misuse incidents; no learning loop; adversarial misuse not considered."
    },

    # =========================================================================
    # A.10 - Third-Party and Customer Relationships (2 controls)
    # =========================================================================
    {
        "id": "A.10.2",
        "title": "Suppliers and third parties",
        "framework": "ISO 42001",
        "category": "A.10 Third-Party Relationships",
        "requirement": "Governance of AI-related third-party relationships including due diligence, contractual requirements, and ongoing oversight of AI components, models, or services sourced externally.",
        "evidence_examples": "AI vendor due diligence questionnaire (covering AI-specific risks); supplier risk assessments; contractual AI clauses; ongoing supplier review; foundation model provider oversight.",
        "common_gaps": "Suppliers used without due diligence; no contractual AI requirements; foundation model providers not assessed; ongoing oversight absent."
    },
    {
        "id": "A.10.3",
        "title": "Responsibilities along the AI life cycle",
        "framework": "ISO 42001",
        "category": "A.10 Third-Party Relationships",
        "requirement": "Where multiple organizations share responsibility for an AI system across its life cycle, responsibilities shall be clearly allocated to prevent gaps at transition points.",
        "evidence_examples": "Documented responsibility allocation across multi-party AI deployments; transition point procedures; contractual responsibilities along the lifecycle; RACI for shared AI systems.",
        "common_gaps": "Responsibility gaps at transition points (developer → deployer → operator); contractual ambiguity in multi-party deployments; no documented handoff procedures."
    },
]