backstory1 = """
    Modern slavery – including forced labour, child labour, human trafficking, and related abuses – has become the target of a number of national laws intended to increase corporate transparency and accountability in global supply chains. Three countries in particular—UK, Australia, and recently Canada—have put in place laws that require certain large entities (companies) to publish annual statements or reports about what steps they have taken to identify, prevent, mitigate, and remediate modern slavery risks in their operations and supply chains.

    Key features common in these regimes include:

    Thresholds of revenue / turnover / number of employees / assets for companies to be in scope. 
    Mandatory content of the statement: business structure, operations, supply chains, risk assessments, policies, training, remedial steps, etc. 

    Requirement that the statements are published publicly, e.g. on the company’s website, and/or submitted to a government register or similar. 

    The UK’s Modern Slavery Act 2015 (section 54: Transparency in Supply Chains) has for many years required covered companies to publish an annual modern slavery / human trafficking / supply chain statement. 
    Australia’s Modern Slavery Act 2018 likewise requires reporting entities to submit to a public online register and publish approved statements. 
    Canada’s relatively new law, the Fighting Against Forced Labour and Child Labour in Supply Chains Act, imposes similar obligations for companies operating in or connected with Canada, including publishing a statement and/or filing a report. 

    Because it's a legal obligation in these jurisdictions, companies’ public websites are expected to have these statements visible (often in a prominent or easily findable place).

"""

goal1 = """
    The agent’s goal is to scrape and analyze official corporate websites of companies that are / may be subject to Modern Slavery / Forced Labour / Child Labour reporting laws in UK, Australia, Canada, in order to corroborate whether these companies have published their required modern slavery reports/statements in compliance with the relevant legal requirements.

    More specifically, the agent should determine:

    Whether a required statement exists (for the most recent reporting year).

    Whether it is published on the company’s website in a discoverable location (e.g. via recognizable link, prominent place, etc.).

    Optionally, whether it appears to satisfy certain minimal legal requirements (e.g. covers risk assessment, supply chain, policies, etc.).

    The agent will be useful for regulatory monitoring, compliance auditing, due diligence, or for ESG / human rights disclosures.
"""


task_description1= """
    Search for a link or page with a modern slavery / forced labour / child labour report or statement (for the most recent year). Terms to look for: “modern slavery statement”, “slavery and human trafficking statement”, “forced labour report”, “child labour report”, etc.

    Verify that the document is published, ideally that it's accessible (not broken link), that it has a date or covers a reporting period (fiscal year), and optionally check for a few of the legally required content items (structure, supply chain, risks, policy, training, remediation).

    If the country law requires registration or submission to a public registry (UK: registry of modern slavery statements; Australia: register; Canada: Public Safety Canada’s submissions / questionnaire), also check whether there is mention/link to that registry or evidence that the report is also filed there.
"""


output1 = """
    The agent’s output will be a comprehensive report detailing the findings of the search and analysis, including whether the required statement was found, where it was located, and whether it appears to satisfy the minimum legal requirements. It will also include any relevant information found on the page, such as the date of the report, the content of the report, and any relevant links or references.
    Also:
        the agent should produce a structured report containing:

        Company name and URL.

        Jurisdiction(s) under which the company is subject to reporting (UK, AU, Canada).

        Whether a modern slavery / forced labour statement/report is publicly published. (Yes / No / Unable to find)

        Date or reporting period of the latest statement (if found).

        The URL(s) or path(s) on the site where the statement is located.

        Whether minimal required elements are present (optional / heuristic check) — e.g.:

        mention of supply chain / operations structure

        risk assessment & risk mitigation steps

        policies in relation to modern slavery / forced labour / child labour

        training or capacity building for staff or suppliers

        remediation measures if issues found

        Whether there is evidence of filing / registration with the official government register (if applicable).

        Any obvious issues (e.g. statement outdated, broken links, missing reporting period, etc.)
"""