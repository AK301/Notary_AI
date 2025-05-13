# backend/prompt_template.py

def deed_prompt(data: dict) -> str:
    return f"""
You are a legal expert helping draft a formal Indian Partnership Deed.

Use the following details to create a legally valid deed:

1. **Firm Name**: {data.get('firm_name')}
2. **Partners**: {', '.join(data.get('partners', []))}
3. **Business Nature**: {data.get('business_type')}
4. **Capital Contributions**: {data.get('capital')}
5. **Profit Sharing Ratio**: {data.get('profit_ratio')}
6. **Commencement Date**: {data.get('start_date')}
7. **Duration**: {data.get('duration')}
8. **Roles & Duties**: {data.get('duties')}
9. **Jurisdiction**: {data.get('jurisdiction')}
10. **Dispute Resolution**: {data.get('dispute_clause')}

Draft the deed in **formal legal language**, formatted in sections and suitable for notary purposes in India.
"""
