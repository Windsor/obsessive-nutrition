#!/usr/bin/env python3
"""Email Deliverability Checker for Ghost newsletters.
Checks SPF, DKIM, DMARC records and reports issues."""
import subprocess
import json
import sys

DOMAINS = {
    "theportugalbrief.pt": "Portugal Brief",
}

DKIM_SELECTORS = [
    "k1", "k2", "k3", "mg", "smtp", "mail", "brevo",
    "google", "default", "s1", "s2", "mandrill", "mailgun",
]


def dig(record_type, domain):
    try:
        r = subprocess.run(
            ["dig", "+short", record_type, domain],
            capture_output=True, text=True, timeout=5,
        )
        return [l.strip().strip('"') for l in r.stdout.strip().split("\n") if l.strip()]
    except Exception:
        return []


def check_domain(domain, name):
    issues = []

    # SPF
    txts = dig("TXT", domain)
    spf = [t for t in txts if "v=spf1" in t]
    if not spf:
        issues.append("CRITICAL: No SPF record found")
    else:
        spf_rec = spf[0]
        if "-all" not in spf_rec and "~all" in spf_rec:
            issues.append("WARNING: SPF uses ~all (softfail) instead of -all (hardfail)")
        if "include:" not in spf_rec:
            issues.append("WARNING: SPF has no include directives - may not cover email provider")
        print("  SPF: " + spf_rec)

    # DMARC
    dmarc = dig("TXT", "_dmarc." + domain)
    if not dmarc:
        issues.append("CRITICAL: No DMARC record found")
    else:
        dmarc_rec = dmarc[0]
        print("  DMARC: " + dmarc_rec)
        if "p=none" in dmarc_rec:
            issues.append("WARNING: DMARC policy is none (monitoring only)")
        if "p=reject" in dmarc_rec:
            print("  DMARC policy: reject OK")

    # DKIM
    found_dkim = False
    for sel in DKIM_SELECTORS:
        result = dig("TXT", sel + "._domainkey." + domain)
        cname = dig("CNAME", sel + "._domainkey." + domain)
        if result or cname:
            found_dkim = True
            print("  DKIM (" + sel + "): found OK")
            break
    if not found_dkim:
        issues.append("CRITICAL: No DKIM record found for any common selector")

    # MX
    mx = dig("MX", domain)
    if mx:
        mx_str = ", ".join(mx)
        print("  MX: " + mx_str)
    else:
        issues.append("WARNING: No MX records")

    return issues


if __name__ == "__main__":
    all_issues = {}
    for domain, name in DOMAINS.items():
        print("\n=== " + name + " (" + domain + ") ===")
        issues = check_domain(domain, name)
        if issues:
            print("\n  Issues (" + str(len(issues)) + "):")
            for i in issues:
                print("    - " + i)
        else:
            print("  All checks passed")
        all_issues[domain] = issues

    if "--json" in sys.argv:
        print(json.dumps(all_issues, indent=2))

    total = sum(len(v) for v in all_issues.values())
    criticals = sum(1 for v in all_issues.values() for i in v if "CRITICAL" in i)
    print("\n--- Summary: " + str(total) + " issues (" + str(criticals) + " critical) ---")

    if criticals:
        print("\nRECOMMENDED ACTIONS:")
        for domain, issues in all_issues.items():
            for i in issues:
                if "DKIM" in i:
                    print("  -> " + domain + ": Set up DKIM with Brevo")
                    print("     Brevo dashboard -> Settings -> Senders & IPs -> Domains -> Authenticate")
                if "SPF" in i and "include" in i:
                    print("  -> " + domain + ": Add 'include:spf.brevo.com' to SPF record")
