"""
Seeds the fictional digital-banking help-center knowledge base.

Run once to generate kb/*.json. This is the "content" the retrieval
systems search over — 16 articles, each carrying governance metadata
(status, owner, last_reviewed, supersedes/superseded_by, taxonomy_path)
on top of the normal title/body a help-center article would have.

Design note: three topics have two versions in the KB — a current
published article and the retired one it replaced, with a genuinely
different number (the policy changed). That's what creates real
staleness risk for retrieval that doesn't look at metadata. There's
also one draft article that has never been reviewed — the content-gap
test case.
"""
import json
import os

ARTICLES = [
    # --- Wire transfers: current + retired pair ---
    {
        "id": "wire-transfer-domestic-limits",
        "title": "Domestic Wire Transfer Limits",
        "taxonomy_path": "Payments > Wire Transfers > Limits",
        "status": "published",
        "owner": "payments-content-team",
        "last_reviewed": "2026-08-12",
        "supersedes": "wire-transfer-domestic-limits-2024",
        "superseded_by": None,
        "body": (
            "The daily limit for outgoing domestic wire transfers is $50,000 "
            "per account for personal banking customers. This limit was raised "
            "from its previous level in August 2026 to accommodate larger "
            "real-estate and business transactions. Transfers above $50,000 "
            "in a single day require splitting across multiple business days "
            "or a call to a banker to request a temporary limit increase. "
            "Wire transfer limit changes take effect immediately once approved "
            "and do not require a new enrollment. Same-day domestic wires "
            "submitted before 4:00 PM ET are typically processed the same "
            "business day."
        ),
    },
    {
        "id": "wire-transfer-domestic-limits-2024",
        "title": "Domestic Wire Transfer Limits (2024)",
        "taxonomy_path": "Payments > Wire Transfers > Limits",
        "status": "retired",
        "owner": "payments-content-team",
        "last_reviewed": "2024-03-01",
        "supersedes": None,
        "superseded_by": "wire-transfer-domestic-limits",
        "body": (
            "The daily limit for outgoing domestic wire transfers is $25,000 "
            "per account for personal banking customers. Customers who need "
            "to send more than $25,000 in a single day must contact a banker "
            "directly to request an exception. Wire transfer limits apply per "
            "account, not per customer, so customers with multiple accounts "
            "may have separate limits on each. Same-day domestic wires "
            "submitted before 3:00 PM ET are typically processed the same "
            "business day."
        ),
    },
    # --- Mobile check deposit: current + retired pair ---
    {
        "id": "mobile-check-deposit-limits",
        "title": "Mobile Check Deposit Limits",
        "taxonomy_path": "Deposits > Mobile Check Deposit > Limits",
        "status": "published",
        "owner": "deposits-content-team",
        "last_reviewed": "2026-07-01",
        "supersedes": "mobile-check-deposit-limits-2023",
        "superseded_by": None,
        "body": (
            "Mobile check deposit limits are $5,000 per check and $10,000 "
            "total per rolling 30-day period for personal accounts in good "
            "standing. Limits are higher for customers with an established "
            "account history of two years or more. Deposited funds are "
            "typically available within one business day, though the first "
            "$500 is often available immediately. Checks must be endorsed "
            "with 'For Mobile Deposit Only' and the account number written "
            "on the back to be accepted."
        ),
    },
    {
        "id": "mobile-check-deposit-limits-2023",
        "title": "Mobile Check Deposit Limits (2023)",
        "taxonomy_path": "Deposits > Mobile Check Deposit > Limits",
        "status": "retired",
        "owner": "deposits-content-team",
        "last_reviewed": "2023-06-15",
        "supersedes": None,
        "superseded_by": "mobile-check-deposit-limits",
        "body": (
            "Mobile check deposit limits are $2,500 per check and $5,000 "
            "total per rolling 30-day period for personal accounts in good "
            "standing. Customers who need higher limits can request an "
            "increase by visiting a branch with two forms of ID. Deposited "
            "funds are typically available within two business days. Checks "
            "must be endorsed with 'For Mobile Deposit Only' to be accepted."
        ),
    },
    # --- Account fees: current + retired pair ---
    {
        "id": "account-maintenance-fees",
        "title": "Monthly Account Maintenance Fees",
        "taxonomy_path": "Accounts > Fees > Maintenance Fees",
        "status": "published",
        "owner": "accounts-content-team",
        "last_reviewed": "2026-02-18",
        "supersedes": "account-maintenance-fees-2023",
        "superseded_by": None,
        "body": (
            "The monthly maintenance fee for a standard checking account is "
            "$12, and is automatically waived for any month with a qualifying "
            "direct deposit of $500 or more, or a minimum daily balance of "
            "$1,500. Savings accounts carry a $5 monthly fee, waived with a "
            "minimum balance of $300. Fee waivers are evaluated at the end of "
            "each statement cycle, so a qualifying deposit posted late in the "
            "cycle still counts."
        ),
    },
    {
        "id": "account-maintenance-fees-2023",
        "title": "Monthly Account Maintenance Fees (2023)",
        "taxonomy_path": "Accounts > Fees > Maintenance Fees",
        "status": "retired",
        "owner": "accounts-content-team",
        "last_reviewed": "2023-01-10",
        "supersedes": None,
        "superseded_by": "account-maintenance-fees",
        "body": (
            "The monthly maintenance fee for a standard checking account is "
            "$15, and is automatically waived for any month with a qualifying "
            "direct deposit of $750 or more. There is no minimum-balance "
            "waiver option for checking accounts. Savings accounts carry a $6 "
            "monthly fee with no waiver available."
        ),
    },
    # --- Other current, published articles ---
    {
        "id": "zelle-transfer-limits",
        "title": "Zelle Transfer Limits",
        "taxonomy_path": "Payments > Zelle > Limits",
        "status": "published",
        "owner": "payments-content-team",
        "last_reviewed": "2026-05-09",
        "supersedes": None,
        "superseded_by": None,
        "body": (
            "Zelle transfers are limited to $2,500 per day and $10,000 per "
            "rolling 30-day period for personal accounts. Business accounts "
            "have separate, higher limits set at account opening. Zelle "
            "transfers to enrolled recipients typically arrive within minutes. "
            "There is no fee to send or receive money via Zelle."
        ),
    },
    {
        "id": "atm-withdrawal-limits",
        "title": "ATM Withdrawal Limits",
        "taxonomy_path": "Accounts > Cards > ATM Withdrawals",
        "status": "published",
        "owner": "cards-content-team",
        "last_reviewed": "2026-06-02",
        "supersedes": None,
        "superseded_by": None,
        "body": (
            "Standard debit cards allow ATM withdrawals of up to $1,000 per "
            "day at in-network ATMs. Out-of-network ATMs may impose a lower "
            "limit set by the ATM operator in addition to the card limit. "
            "Customers can request a temporary limit increase for travel by "
            "contacting support or adjusting the limit in the mobile app "
            "under Card Controls."
        ),
    },
    {
        "id": "overdraft-protection-options",
        "title": "Overdraft Protection Options",
        "taxonomy_path": "Accounts > Overdraft > Protection Options",
        "status": "published",
        "owner": "accounts-content-team",
        "last_reviewed": "2026-04-22",
        "supersedes": None,
        "superseded_by": None,
        "body": (
            "Overdraft protection can be linked from a savings account or a "
            "credit line to cover transactions that would otherwise overdraw "
            "checking. Transfers from a linked savings account carry no fee. "
            "Transfers from a linked credit line are treated as a cash advance "
            "and accrue interest from the transfer date. Customers can opt in "
            "or out of overdraft coverage for everyday debit card purchases "
            "at any time in account settings."
        ),
    },
    {
        "id": "card-dispute-process",
        "title": "How to Dispute a Card Charge",
        "taxonomy_path": "Accounts > Cards > Disputes",
        "status": "published",
        "owner": "cards-content-team",
        "last_reviewed": "2026-03-11",
        "supersedes": None,
        "superseded_by": None,
        "body": (
            "To dispute a card charge, open the transaction in the mobile app "
            "and select 'Dispute this charge,' or call support. Disputes must "
            "generally be filed within 60 days of the statement date on which "
            "the charge appeared. Provisional credit is typically issued "
            "within 10 business days while the dispute is investigated, and "
            "the investigation itself can take up to 90 days for complex "
            "cases."
        ),
    },
    {
        "id": "international-wire-transfer-fees",
        "title": "International Wire Transfer Fees",
        "taxonomy_path": "Payments > Wire Transfers > International",
        "status": "published",
        "owner": "payments-content-team",
        "last_reviewed": "2026-01-20",
        "supersedes": None,
        "superseded_by": None,
        "body": (
            "Outgoing international wire transfers carry a $45 fee, plus any "
            "fees charged by intermediary or receiving banks, which the "
            "sender does not control. International wires are typically sent "
            "in the recipient's local currency at the exchange rate in effect "
            "at the time of transfer. Delivery usually takes one to five "
            "business days depending on the destination country."
        ),
    },
    {
        "id": "two-factor-authentication-setup",
        "title": "Setting Up Two-Factor Authentication",
        "taxonomy_path": "Security > Account Access > Two-Factor Authentication",
        "status": "published",
        "owner": "security-content-team",
        "last_reviewed": "2025-12-05",
        "supersedes": None,
        "superseded_by": None,
        "body": (
            "Two-factor authentication can be enabled in Security Settings in "
            "the mobile app or website. Supported second factors include SMS "
            "codes, an authenticator app, or a physical security key. Once "
            "enabled, a second factor is required any time you sign in from a "
            "new device. Backup codes should be saved somewhere safe in case "
            "the primary second factor is unavailable."
        ),
    },
    {
        "id": "joint-account-management",
        "title": "Managing a Joint Account",
        "taxonomy_path": "Accounts > Account Types > Joint Accounts",
        "status": "published",
        "owner": "accounts-content-team",
        "last_reviewed": "2025-11-14",
        "supersedes": None,
        "superseded_by": None,
        "body": (
            "Either owner on a joint account can make transactions, view "
            "statements, and manage account settings independently unless the "
            "account was set up requiring both signatures. Removing a joint "
            "owner requires a branch visit with ID for both account holders. "
            "Either owner can close the account without the other's consent "
            "unless the account agreement specifies otherwise."
        ),
    },
    {
        "id": "account-closure-process",
        "title": "How to Close Your Account",
        "taxonomy_path": "Accounts > Account Management > Closing an Account",
        "status": "published",
        "owner": "accounts-content-team",
        "last_reviewed": "2025-10-02",
        "supersedes": None,
        "superseded_by": None,
        "body": (
            "To close an account, the balance must first be zeroed out by "
            "transfer or withdrawal, and all pending transactions and "
            "automatic payments must clear. Accounts can be closed by phone, "
            "in a branch, or through secure chat, but not through the mobile "
            "app directly. Closing an account does not affect your credit "
            "score unless it carries a negative balance sent to collections."
        ),
    },
    {
        "id": "mobile-check-deposit-troubleshooting",
        "title": "Mobile Check Deposit: Troubleshooting a Rejected Deposit",
        "taxonomy_path": "Deposits > Mobile Check Deposit > Troubleshooting",
        "status": "published",
        "owner": "deposits-content-team",
        "last_reviewed": "2026-06-20",
        "supersedes": None,
        "superseded_by": None,
        "body": (
            "If a mobile check deposit is rejected, the most common causes "
            "are a missing or incorrect endorsement, a blurry photo of the "
            "check, or a stale-dated check (older than six months). Rejected "
            "deposits are not charged against your deposit limit. Re-take the "
            "photo in good lighting on a dark, flat surface and confirm the "
            "endorsement includes 'For Mobile Deposit Only' before "
            "resubmitting. If the issue persists, deposit the check in person "
            "at a branch or ATM instead."
        ),
    },
    # --- Draft, never reviewed: content-gap test ---
    {
        "id": "student-checking-benefits-draft",
        "title": "Student Checking Account Benefits (DRAFT)",
        "taxonomy_path": "Accounts > Account Types > Student Checking",
        "status": "draft",
        "owner": "accounts-content-team",
        "last_reviewed": None,
        "supersedes": None,
        "superseded_by": None,
        "body": (
            "DRAFT — NOT YET REVIEWED. Proposed benefits for the new Student "
            "Checking account: no monthly maintenance fee while enrolled in "
            "school, no minimum balance requirement, and up to two ATM fee "
            "rebates per statement cycle. Eligibility, verification process, "
            "and the exact ATM rebate amount are still being finalized with "
            "legal and are not confirmed. Do not publish or quote these terms "
            "to customers until this article is reviewed and approved."
        ),
    },
]


def main():
    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "kb")
    os.makedirs(out_dir, exist_ok=True)
    for article in ARTICLES:
        path = os.path.join(out_dir, f"{article['id']}.json")
        with open(path, "w") as f:
            json.dump(article, f, indent=2)
            f.write("\n")
    print(f"Wrote {len(ARTICLES)} articles to {out_dir}/")


if __name__ == "__main__":
    main()
