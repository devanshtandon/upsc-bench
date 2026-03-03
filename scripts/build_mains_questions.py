#!/usr/bin/env python3
"""Build the UPSC Mains 2025 question dataset from collected data."""

import json
import re
from pathlib import Path


def build_mains_2025():
    questions = []

    # ============================================================
    # ESSAY PAPER (8 topics, 2 sections)
    # ============================================================
    essay_topics = {
        "A": [
            "Truth knows no color.",
            "The supreme art of war is to subdue the enemy without fighting.",
            "Thought finds a world and creates one also.",
            "Best lessons are learnt through bitter experiences.",
        ],
        "B": [
            "Muddy water is best cleared by leaving it alone.",
            "The years teach much which the days never know.",
            "It is best to see life as a journey, not as a destination.",
            "Contentment is natural wealth; luxury is artificial poverty.",
        ],
    }

    q_num = 0
    for section, topics in essay_topics.items():
        for i, topic in enumerate(topics, 1):
            q_num += 1
            questions.append({
                "id": f"mains_essay_2025_q{q_num}",
                "year": 2025,
                "paper": "mains_essay",
                "section": section,
                "question_number": q_num,
                "question_text": topic,
                "word_limit": 1200,
                "max_marks": 125,
                "question_type": "essay",
            })

    # ============================================================
    # GS PAPER 1 (20 questions)
    # ============================================================
    gs1_questions = [
        # 10-mark questions (Q1-Q10, 150 words)
        ("Discuss the salient features of the Harappan architecture.", 10, 150),
        ("Examine the main aspects of Akbar's religious syncretism.", 10, 150),
        ("'The sculptors filled the Chandella artform with resilient vigor and breadth of life.' Elucidate.", 10, 150),
        ("How are climate change and the sea level rise affecting the very existence of many island nations? Discuss with examples.", 10, 150),
        ("What are non-farm primary activities? How are these activities related to physiographic features in India? Discuss with suitable examples.", 10, 150),
        ("Explain briefly the ecological and economic benefits of solar energy generation in India with suitable examples.", 10, 150),
        ("What are Tsunamis? How and where are they formed? What are their consequences? Explain with examples.", 10, 150),
        ("How does smart city in India, address the issues of urban poverty and distributive justice?", 10, 150),
        ("The ethos of civil service in India stands for the combination of professionalism with nationalistic consciousness \u2013 Elucidate.", 10, 150),
        ("Do you think that globalization results in only an aggressive consumer culture? Justify your answer.", 10, 150),
        # 15-mark questions (Q11-Q20, 250 words)
        ("Mahatma Jotirao Phule's writings and efforts of social reforms touched issues of almost all subaltern classes. Discuss.", 15, 250),
        ("Trace India's consolidation process during early phase of independence in terms of polity, economy, education and international relations.", 15, 250),
        ("The French Revolution has enduring relevance to the contemporary world. Explain.", 15, 250),
        ("Give a geographical explanation of the distribution of off-shore oil reserves of the world. How are they different from the on-shore occurrences of oil reserves?", 15, 250),
        ("How can Artificial Intelligence (AI) and drones be effectively used along with GIS and RS techniques in locational and areal planning?", 15, 250),
        ("Discuss how the changes in shape and sizes of continents and ocean basins of the planet take place due to tectonic movements of the crustal masses.", 15, 250),
        ("Discuss the distribution and density of population in the Ganga River Basin with special reference to land, soil and water resources.", 15, 250),
        ("How do you account for the growing fast food industries given that there are increased health concerns in modern society? Illustrate your answer with the Indian experience.", 15, 250),
        ("Achieving sustainable growth with emphasis on environmental protection could come into conflict with poor people's needs in a country like India \u2013 Comment.", 15, 250),
        ("Does tribal development in India centre around two axes, those of displacement and of rehabilitation? Give your opinion.", 15, 250),
    ]

    for i, (text, marks, words) in enumerate(gs1_questions, 1):
        questions.append({
            "id": f"mains_gs1_2025_q{i}",
            "year": 2025,
            "paper": "mains_gs1",
            "section": None,
            "question_number": i,
            "question_text": text,
            "word_limit": words,
            "max_marks": marks,
            "question_type": "short_answer",
        })

    # ============================================================
    # GS PAPER 2 (20 questions)
    # ============================================================
    gs2_questions = [
        # 10-mark questions (Q1-Q10, 150 words)
        ("Discuss the 'corrupt practices' for the purpose of the Representation of the People Act, 1951. Analyze whether the increase in the assets of the legislators and/or their associates, disproportionate to their known sources of income, would constitute 'undue influence' and consequently a corrupt practice.", 10, 150),
        ("Comment on the need of administrative tribunals as compared to the court system. Assess the impact of the recent tribunal reforms through rationalization of tribunals made in 2021.", 10, 150),
        ("Compare and contrast the President's power to pardon in India and in the USA. Are there any limits to it in both the countries? What are 'preemptive pardons'?", 10, 150),
        ("Discuss the nature of Jammu and Kashmir Legislative Assembly after the Jammu and Kashmir Reorganization Act, 2019. Briefly describe the powers and functions of the Assembly of the Union Territory of Jammu and Kashmir.", 10, 150),
        ("\"The Attorney General of India plays a crucial role in guiding the legal framework of the Union Government and ensuring sound governance through legal counsel.\" Discuss his responsibilities, rights and limitations in this regard.", 10, 150),
        ("Women's social capital complements in advancing empowerment and gender equity. Explain.", 10, 150),
        ("e-governance projects have a built-in bias towards technology and back-end integration than user-centric designs. Examine.", 10, 150),
        ("Civil Society Organizations are often perceived as being anti-State actors than non-State actors. Do you agree? Justify.", 10, 150),
        ("India-Africa digital partnership is achieving mutual respect, co-development and long-term institutional partnerships. Elaborate.", 10, 150),
        ("\"With the waning of globalization, post-Cold War world is becoming a site of sovereign nationalism.\" Elucidate.", 10, 150),
        # 15-mark questions (Q11-Q20, 250 words)
        ("\"Constitutional morality is the fulcrum which acts as an essential check upon the high functionaries and citizens alike\u2026\" In view of the above observation of the Supreme Court, explain the concept of constitutional morality and its application to ensure balance between judicial independence and judicial accountability in India.", 15, 250),
        ("Indian Constitution has conferred the amending power on the ordinary legislative institutions with a few procedural hurdles. In view of this statement, examine the procedural and substantive limitations on the amending power of the Parliament to change the Constitution.", 15, 250),
        ("Discuss the evolution of collegium system in India. Critically examine the advantages and disadvantages of the system of appointment of the Judges of the Supreme Court of India and that of the USA.", 15, 250),
        ("Examine the evolving pattern of Centre-State financial relations in the context of planned development in India. How far have the recent reforms impacted the fiscal federalism in India?", 15, 250),
        ("What are environmental pressure groups? Discuss their role in raising awareness, influencing policies and advocating for environmental protection in India.", 15, 250),
        ("Inequality in the ownership pattern of resources is one of the major causes of poverty. Discuss in the context of 'paradox of poverty'.", 15, 250),
        ("\"In contemporary development models, decision-making and problem-solving responsibilities are not located close to the source of information and execution defeating the objectives of development.\" Critically evaluate.", 15, 250),
        ("The National Commission for Protection of Child Rights has to address the challenges faced by children in the digital era. Examine the existing policies and suggest measures the Commission can initiate to tackle the issue.", 15, 250),
        ("\"Energy security constitutes the dominant kingpin of India's foreign policy, and is linked with India's overarching influence in Middle Eastern countries.\" How would you integrate energy security with India's foreign policy trajectories in the coming years?", 15, 250),
        ("\"The reform process in the United Nations remains unresolved, because of the delicate imbalance of East and West and entanglement of the USA vs. Russo-Chinese alliance.\" Examine and critically evaluate the East-West policy confrontations in this regard.", 15, 250),
    ]

    for i, (text, marks, words) in enumerate(gs2_questions, 1):
        questions.append({
            "id": f"mains_gs2_2025_q{i}",
            "year": 2025,
            "paper": "mains_gs2",
            "section": None,
            "question_number": i,
            "question_text": text,
            "word_limit": words,
            "max_marks": marks,
            "question_type": "short_answer",
        })

    # ============================================================
    # GS PAPER 3 (20 questions)
    # ============================================================
    gs3_questions = [
        # 10-mark questions (Q1-Q10, 150 words)
        ("Distinguish between the Human Development Index (HDI) and the Inequality-adjusted Human Development Index (IHDI) with special reference to India. Why is the IHDI considered a better indicator of inclusive development?", 10, 150),
        ("What are the challenges before the Indian economy when the world is moving away from free trade and multilateralism to protectionism and bilateralism? How can these challenges be met?", 10, 150),
        ("Explain the factors influencing the decision of the farmers on the selection of high value crops in India.", 10, 150),
        ("Elaborate the scope and significance of supply chain management of agricultural commodities in India.", 10, 150),
        ("The fusion energy programme in India has steadily evolved over the past few decades. Mention India's contributions to the international fusion energy project \u2013 International Thermonuclear Experimental Reactor (ITER). Describe the future prospects of fusion energy for India.", 10, 150),
        ("How can India achieve energy independence through clean technology by 2047? How can biotechnology play a crucial role in this endeavour?", 10, 150),
        ("What is Carbon Capture, Utilization and Storage (CCUS)? What is the potential role of CCUS in tackling climate change?", 10, 150),
        ("Seawater intrusion in the coastal aquifers is a major concern in India. What are the causes of seawater intrusion and the remedial measures to combat this hazard?", 10, 150),
        ("Terrorism is a global scourge. How has it manifested in India? Elaborate with contemporary examples. What are the counter measures adopted by the State? Explain.", 10, 150),
        ("The Government of India recently stated that Left Wing Extremism (LWE) will be eliminated by 2026. What do you understand by LWE and how are the people affected by it? What measures have been taken to address this challenge?", 10, 150),
        # 15-mark questions (Q11-Q20, 250 words)
        ("Explain how the Fiscal Health Index (FHI) can be used as a tool for assessing the fiscal performance of states in India. In what way would it encourage the states to adopt prudent and sustainable fiscal policies?", 15, 250),
        ("Discuss the rationale of the Production Linked Incentive (PLI) scheme. What are its achievements? In what way can the functioning and outcomes of the scheme be improved?", 15, 250),
        ("Examine the factors responsible for depleting groundwater in India. What are the steps taken by the government to mitigate such depletion of groundwater?", 15, 250),
        ("Examine the scope of the food processing industries in India. Elaborate the measures taken by the government in the food processing industries for generating employment opportunities.", 15, 250),
        ("How does nanotechnology offer significant advancements in the field of agriculture? How can this technology help to uplift the socio-economic status of farmers?", 15, 250),
        ("India aims to become a semiconductor manufacturing hub. What are the challenges faced by the semiconductor industry in India? Mention the salient features of the India Semiconductor Mission.", 15, 250),
        ("Mineral resources are fundamental to the country's economy and these are exploited by mining. Why is mining considered an environmental hazard? Explain the remedial measures required to reduce the environmental hazard due to mining.", 15, 250),
        ("Write a review on India's climate commitments under the Paris Agreement (2015) and mention how these have been further strengthened in COP26 (2021). In this direction, how has the first Nationally Determined Contribution intended by India been updated in 2022?", 15, 250),
        ("What are the major challenges to internal security and peace process in the North-Eastern States? Map the various peace accords and agreements initiated by the government in the past decade.", 15, 250),
        ("Why is maritime security vital to protect India's sea trade? Discuss maritime and coastal security challenges and the way forward.", 15, 250),
    ]

    for i, (text, marks, words) in enumerate(gs3_questions, 1):
        questions.append({
            "id": f"mains_gs3_2025_q{i}",
            "year": 2025,
            "paper": "mains_gs3",
            "section": None,
            "question_number": i,
            "question_text": text,
            "word_limit": words,
            "max_marks": marks,
            "question_type": "short_answer",
        })

    # ============================================================
    # GS PAPER 4 - Ethics (12 questions)
    # Section A: Theoretical (Q1-Q6, 10 marks each, some multi-part)
    # Section B: Case Studies (Q7-Q12, 20 marks each)
    # ============================================================
    gs4_theoretical = [
        # Q1 (two parts, 10 marks each)
        {
            "id": "mains_gs4_2025_q1a",
            "question_number": 1,
            "question_text": "In the present digital age, social media has revolutionised our way of communication and interaction. However, it has raised several ethical issues and challenges. Describe the key ethical dilemmas in this regard.",
            "max_marks": 10,
            "word_limit": 150,
            "section": "A",
            "question_type": "short_answer",
        },
        {
            "id": "mains_gs4_2025_q1b",
            "question_number": 1,
            "question_text": "\"Constitutional morality is not a natural sentiment but a product of civil education and adherence of the rule of law.\" Examine the significance of constitutional morality for public servants, highlighting the role in promoting good governance and ensuring accountability in public administration.",
            "max_marks": 10,
            "word_limit": 150,
            "section": "A",
            "question_type": "short_answer",
        },
        # Q2 (two parts, 10 marks each)
        {
            "id": "mains_gs4_2025_q2a",
            "question_number": 2,
            "question_text": "Carl von Clausewitz once said, \"War is a diplomacy by other means.\" Critically analyse the above statement in the present context of contemporary geo-political conflict.",
            "max_marks": 10,
            "word_limit": 150,
            "section": "A",
            "question_type": "short_answer",
        },
        {
            "id": "mains_gs4_2025_q2b",
            "question_number": 2,
            "question_text": "Keeping the national security in mind, examine the ethical dilemmas related to controversial orders of environmental clearance of developmental projects in ecologically sensitive border areas in the country.",
            "max_marks": 10,
            "word_limit": 150,
            "section": "A",
            "question_type": "short_answer",
        },
        # Q3 (three quotations, 10 marks each)
        {
            "id": "mains_gs4_2025_q3a",
            "question_number": 3,
            "question_text": "\"Those who in trouble untroubled are, will trouble trouble itself.\" \u2013 Thiruvalluvar. What does this quotation convey to you in the present context?",
            "max_marks": 10,
            "word_limit": 150,
            "section": "A",
            "question_type": "short_answer",
        },
        {
            "id": "mains_gs4_2025_q3b",
            "question_number": 3,
            "question_text": "\"The greatest discovery of my generation is that a human being can alter his life by altering his attitudes.\" \u2013 William James. What does this quotation convey to you in the present context?",
            "max_marks": 10,
            "word_limit": 150,
            "section": "A",
            "question_type": "short_answer",
        },
        {
            "id": "mains_gs4_2025_q3c",
            "question_number": 3,
            "question_text": "\"The strength of a society is not in its laws, but in the morality of its people.\" \u2013 Swami Vivekananda. What does this quotation convey to you in the present context?",
            "max_marks": 10,
            "word_limit": 150,
            "section": "A",
            "question_type": "short_answer",
        },
        # Q4 (two parts, 10 marks each)
        {
            "id": "mains_gs4_2025_q4a",
            "question_number": 4,
            "question_text": "\"For any kind of social re-engineering by successfully implementing welfare schemes, a civil servant must use reason and critical thinking in an ethical framework.\" Justify this statement with suitable examples.",
            "max_marks": 10,
            "word_limit": 150,
            "section": "A",
            "question_type": "short_answer",
        },
        {
            "id": "mains_gs4_2025_q4b",
            "question_number": 4,
            "question_text": "What are the major teachings of Mahavira? Explain their relevance in the contemporary world.",
            "max_marks": 10,
            "word_limit": 150,
            "section": "A",
            "question_type": "short_answer",
        },
        # Q5 (two parts, 10 marks each)
        {
            "id": "mains_gs4_2025_q5a",
            "question_number": 5,
            "question_text": "\"One who is devoted to one's duty attains highest perfection in life.\" Analyse this statement with reference to sense of responsibility and personal fulfilment in a civil servant.",
            "max_marks": 10,
            "word_limit": 150,
            "section": "A",
            "question_type": "short_answer",
        },
        {
            "id": "mains_gs4_2025_q5b",
            "question_number": 5,
            "question_text": "To achieve holistic development goals, a civil servant acts as an enabler and active facilitator of growth rather than a regulator. What specific measures will you suggest to achieve this goal?",
            "max_marks": 10,
            "word_limit": 150,
            "section": "A",
            "question_type": "short_answer",
        },
        # Q6 (two parts, 10 marks each)
        {
            "id": "mains_gs4_2025_q6a",
            "question_number": 6,
            "question_text": "It is said that for a sound ethical work culture, there must be code of ethics in place in every organisation. To ensure value-based work culture, what suitable measures would you adopt in your work place?",
            "max_marks": 10,
            "word_limit": 150,
            "section": "A",
            "question_type": "short_answer",
        },
        {
            "id": "mains_gs4_2025_q6b",
            "question_number": 6,
            "question_text": "India is an emerging economic power of the world. For IMF's Projection, India has recently secured the status of fourth largest economy of the world. At the same time, certain concerns have been observed in some sectors, including food security, energy, environment or instability. What recommendations will you give within an ethical framework for sustainable economic growth of the country?",
            "max_marks": 10,
            "word_limit": 150,
            "section": "A",
            "question_type": "short_answer",
        },
    ]

    for q in gs4_theoretical:
        questions.append({
            "id": q["id"],
            "year": 2025,
            "paper": "mains_gs4",
            "section": q["section"],
            "question_number": q["question_number"],
            "question_text": q["question_text"],
            "word_limit": q["word_limit"],
            "max_marks": q["max_marks"],
            "question_type": q["question_type"],
        })

    # GS4 Section B: Case Studies (Q7-Q12, 20 marks each, 250 words)
    gs4_case_studies = [
        {
            "id": "mains_gs4_2025_q7",
            "question_number": 7,
            "question_text": "Vijay was Deputy Commissioner of remote district of Hilly Northern State of the country for the last two years. In the month of August heavy rains lashed the complete state followed by cloud burst in the upper reaches of the said district. The damage was very heavy in the complete state especially the said district. Vijay took control of the situation very well by using all resources at his disposal and proactive efforts. He received a phone call from his wife that their house is likely to be affected by rains and likely to damage severely and needs his attention. Vijay has a family, wife and school going children. He is in a dilemma as his family is in one corner and the affected people and his duty as a Deputy Commissioner is on the other. (a) What are the options available with Vijay? (b) What are the ethical dilemmas being faced by Vijay? (c) Critically evaluate and examine each of these options identified by Vijay. (d) Which of the options, do you think, would be most appropriate for Vijay to adopt and why?",
            "max_marks": 20,
            "word_limit": 250,
        },
        {
            "id": "mains_gs4_2025_q8",
            "question_number": 8,
            "question_text": "In line with the Directive Principles of State Policy enshrined in the Indian Constitution, the government has a constitutional obligation to ensure basic needs \u2013 Roti, Kapda aur Makaan (Food, Clothes and Shelter) \u2013 for the under-privileged. Pursuing this mandate, the district administration proposed clearing a stretch of forest land to construct low-cost houses for the homeless population. The project could provide permanent shelter and basic services to thousands of vulnerable families. However, this stretch of forest plays a critical role in the local ecosystem. The forests provide habitat for wildlife, support soil fertility and prevent land/soil erosion and sustain livelihoods of tribal and nomadic communities. In spite of the ecological and social costs, the administration argues in favour of the proposal by highlighting that this way vulnerable groups' fundamental human rights enjoy a vital welfare priority. Besides, it fulfils the government's duty to uplift and empower the poor through inclusive development. Therefore, forest clearance has been sought for these works and many departments and civil society groups have also endorsed the same because it may help to curb anti-social elements. (a) Can deforestation be ethically justified in the pursuit of social welfare objectives like housing for the homeless? (b) What are the socio-economic, administrative and ethical challenges in ensuring environment conservation with humane development? (c) What substantial alternatives or policy interventions can be proposed to ensure that both environment integrity and human development are protected?",
            "max_marks": 20,
            "word_limit": 250,
        },
        {
            "id": "mains_gs4_2025_q9",
            "question_number": 9,
            "question_text": "Subash is Secretary, PWD in the State Government. He is a senior officer, known for his competence, integrity and dedication to work. He enjoys the trust and confidence of Minister in charge of PWD and Program Implementation. As a part of his job profile, he is responsible for policy formulation, execution of projects relating to infrastructure initiatives in the State. Subash's Minister is an important Minister in the state and significant growth in urban infrastructure development and road network has been registered during his tenure. He is very keen for launching of ambitious road construction project in near future. Subash's only son Vikas is in real estate business. His son is aware that a mega road project is on the anvil. He is very keen to buy a vast land that can be near the location of the upcoming project, knowing that there would be a quantum jump in land prices. Vikas has contacted his father to share the location of the proposed project and assured him of making him a director in his business. The Minister has also introduced his nephew with big real estate interests and indirectly indicated Subash to take care of his nephew's issues with respect to the forthcoming project. (a) Discuss the ethical issues involved in the case. (b) Critically examine the options available to Subash in the above situation. (c) Which of the above would be most appropriate and why?",
            "max_marks": 20,
            "word_limit": 250,
        },
        {
            "id": "mains_gs4_2025_q10",
            "question_number": 10,
            "question_text": "Rajesh is a Group A officer with nine years of service. He is posted as Administrative Officer in an Oil Public Sector undertaking. As an Administrative Officer he is responsible for managing and coordinating various administrative tasks. Rajesh is expecting his next promotion in JAG in the next one or two years, which is based on ACRs of the last few years. One day his immediate boss (reporting officer for ACR) wants him to buy extra stationary on priority from a particular vendor. Rajesh disallows this initiative at first instance. However, after repeated insistence, Rajesh brings in the assistance of two Group Three Employees and all stationary items are purchased from the same vendor as per GFR tendering. The reporting officer remained silent but his facial expression suggested dissatisfaction. Rajesh is now apprehending adverse remarks in his ACR consequent upon his refusal. (a) What are the options available with Rajesh in the above situation? (b) What are the ethical issues involved in this case? (c) Which would be the most appropriate option for Rajesh and why?",
            "max_marks": 20,
            "word_limit": 250,
        },
        {
            "id": "mains_gs4_2025_q11",
            "question_number": 11,
            "question_text": "Mahatma Gandhi National Rural Employment Guarantee Program (MGNREGA) is an Indian Social Welfare Program that aimed at fulfilling the \"Right to Work\" provisions. You have been appointed as Administrator Incharge of the District with responsibility of monitoring MGNREGA work undertaken by various Gram Panchayats. You notice that your predecessor has mismanaged the Program in terms of: (i) Money not disbursed to actual job-seekers. (ii) Muster Rolls of the Labourers not properly maintained. (iii) Mismatch between the work done and payments made. (iv) Payments made to fictitious persons. (v) Job Cards were given without looking into the need of person. (vi) Mismanagement of funds and siphoning of funds. (vii) Approved works that never existed. (a) What is your reaction to the above situation and how do you restore the proper functioning of MGNREGA Program in this regard? (b) What actions would you initiate to solve the various issues listed above? (c) How would you deal with the above situation?",
            "max_marks": 20,
            "word_limit": 250,
        },
        {
            "id": "mains_gs4_2025_q12",
            "question_number": 12,
            "question_text": "Ashok is Divisional Commissioner of one of the border districts of the North East State. Military has taken over the neighbouring country after overthrowing the elected civil government. Due to intense fight between military and rebel groups, civilian casualties have increased. One night Ashok gets information that nearly 200-250 people, mainly women and children, are trying to cross over to our side at the border. There are also about 10 soldiers with weapons in military uniform who want to cross over. Women and children are crying and begging for help; some are injured and need immediate medical attention. The Minister wants an immediate report. Ashok tried to contact the Home Secretary but failed due to poor connectivity. (a) What are the options available with Ashok to cope with the situation? (b) What are the ethical and legal dilemmas being faced by Ashok? (c) Which of the options, do you think would be more appropriate for Ashok to adopt and why? (d) In the present situation, what are the extra precautionary measures to be taken by the Border Guarding Police in dealing with soldiers in uniform?",
            "max_marks": 20,
            "word_limit": 250,
        },
    ]

    for q in gs4_case_studies:
        questions.append({
            "id": q["id"],
            "year": 2025,
            "paper": "mains_gs4",
            "section": "B",
            "question_number": q["question_number"],
            "question_text": q["question_text"],
            "word_limit": q["word_limit"],
            "max_marks": q["max_marks"],
            "question_type": "case_study",
        })

    return questions


if __name__ == "__main__":
    questions = build_mains_2025()

    output_path = Path("data/mains_questions/mains_2025.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)

    # Print summary
    papers = {}
    for q in questions:
        p = q["paper"]
        papers[p] = papers.get(p, 0) + 1

    total_marks = sum(q["max_marks"] for q in questions)
    print(f"Total questions: {len(questions)}")
    print(f"Total marks: {total_marks}")
    for paper, count in sorted(papers.items()):
        paper_marks = sum(q["max_marks"] for q in questions if q["paper"] == paper)
        print(f"  {paper}: {count} questions, {paper_marks} marks")
    print(f"\nSaved to {output_path}")
