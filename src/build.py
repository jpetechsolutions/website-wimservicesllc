#!/usr/bin/env python3
"""
Build the WIM Services, LLC static site.

    python3 src/build.py

Writes every page into public/. All page copy lives in this file.
Facts here are sourced from Warren Merrill's own published profiles
(wbmconsulting.co, IBBA, BizQuest, BizBuySell) — see NOTES.md.
"""

import hashlib
import json
import os
import re
import shutil
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
PUB = os.path.join(ROOT, "public")

# --------------------------------------------------------------------------
# site constants
# --------------------------------------------------------------------------

SITE = {
    "name": "WIM Services, LLC",
    "short": "WIM Services",
    "dba": "WBM Consulting",
    "person": "Warren B. Merrill",
    "role": "General Manager & Business Broker",
    "tagline": "Trust is the strength of healthy relationships.",
    "domain": "wimservicesllc.com",
    "base": "https://wimservicesllc.com",
    "tel_display": "360.904.4060",
    "tel_href": "+13609044060",
    "email": "warren@wimservicesllc.com",
    "broker_lic": "BK-3514191",
    "brokerage_lic": "CQ-1074384",
    "cam_lic": "CAM 65979",
    "cab_lic": "CAB 6746",
    # Address of record on Sunbiz, all four DBPR licences, IBBA, BBF and the
    # Google Business Profile. The Sarasota and E Pine Street addresses on
    # Warren's signature block are not on any public record — confirm before
    # publishing them. See NOTES.md.
    "offices": [
        {
            "city": "Orlando",
            "street": "151 E Washington Street, Suite 219",
            "locality": "Orlando",
            "region": "FL",
            "zip": "32801",
        },
    ],
    "social": {
        "linkedin": "https://www.linkedin.com/in/warren-merrill-679b1a6a/",
        "facebook": "https://www.facebook.com/wbmconsulting/",
        "bizbuysell": "https://www.bizbuysell.com/business-broker/warren-merrill/wim-services-llc/43778/",
        "bizquest": "https://www.bizquest.com/business-broker/wim-services-llc/warren-merrill/BW52271/",
    },
    # Leave empty until a Web3Forms key is created for Warren's inbox.
    # With no key the form tells visitors to call, text or email instead.
    "web3forms_key": "",
    # Leave empty until GA4 is set up for this domain.
    "ga4_id": "",
}

YEAR = date.today().year

NAV = [
    ("/about", "About"),
    ("/selling-a-business", "Selling"),
    ("/buying-a-business", "Buying"),
    ("/industries", "Industries"),
    ("/listings", "Listings"),
    ("/contact", "Contact"),
]

# --------------------------------------------------------------------------
# shared content
# --------------------------------------------------------------------------

INDUSTRIES = [
    ("Business &amp; B2B Services", "Staffing, facilities, logistics support, commercial service routes and recurring-contract businesses."),
    ("Professional Services", "CPA and accounting practices, consultancies, agencies, insurance books and licensed practices."),
    ("Construction &amp; Trades", "General and specialty contractors, site work, mechanical, electrical and plumbing businesses."),
    ("Manufacturing &amp; Wholesale", "Light manufacturing, fabrication, distribution and import/wholesale operations."),
    ("Restaurants &amp; Liquor Licenses", "Independent restaurants, bars and quota liquor licenses in Central and South Florida."),
    ("Health Care &amp; Social Assistance", "Clinics, home care, therapy practices and allied health services."),
    ("Industrial &amp; Technical Services", "Field service, industrial maintenance, environmental and specialty technical firms."),
    ("Logistics &amp; Transportation", "Freight, last-mile, specialty hauling and equipment-based operations."),
    ("Finance &amp; Insurance", "Agencies, books of business and finance-adjacent service companies."),
    ("Real Estate Rental &amp; Leasing", "Property service businesses, equipment rental and leasing operations."),
]

PRINCIPLES = [
    (
        "doc",
        "Thoughtful preparation",
        "Before anything goes to market, we build the case for your business — recast financials, "
        "clean numbers, defensible positioning and a clear story a buyer and a lender can both follow. "
        "Deals fall apart in due diligence when preparation was thin.",
    ),
    (
        "chat",
        "Clear communication",
        "You get regular updates and the reasoning behind every recommendation, from listing through "
        "closing. No silence, no surprises, and a straight answer when the answer is not the one "
        "you were hoping for.",
    ),
    (
        "target",
        "Disciplined execution",
        "The goal is not the most offers — it is the right buyer at the right price on terms that "
        "actually survive closing and funding. That takes screening buyers properly and holding the "
        "line on structure.",
    ),
]

SELL_STEPS = [
    (
        "Consultation, financial review &amp; valuation",
        "A confidential conversation about your business, your goals and your timeline. We review "
        "roughly three years of financial statements plus current year-to-date results, recast "
        "owner benefit, and set a realistic market position — not a flattering number that "
        "stalls the listing for a year.",
    ),
    (
        "Positioning &amp; confidential marketing",
        "We prepare a confidential information memorandum and a buyer-ready listing that leads with "
        "the strengths a buyer underwrites. Marketing is discreet and targeted, so your employees, "
        "customers, landlord and competitors are not the ones who find out you are selling.",
    ),
    (
        "Buyer qualification",
        "Every prospect is screened for seriousness and financial capacity. Before any detailed "
        "information is released, a buyer signs a non-disclosure agreement and provides proof of "
        "funds or demonstrated financing capability.",
    ),
    (
        "Offers, negotiation &amp; due diligence",
        "We evaluate offers on structure as well as headline price — cash at close, seller note, "
        "earn-out, holdbacks, working-capital treatment, lease assignment and transition terms. "
        "Then we support the buyer's diligence so it confirms what was represented.",
    ),
    (
        "Closing &amp; transition",
        "Closing is coordinated with experienced closing attorneys. Ownership transfers, funds are "
        "disbursed, and the handover — including training and any agreed consulting period — is "
        "managed so the business keeps running.",
    ),
]

BUY_STEPS = [
    (
        "Understanding your objectives",
        "We start with what you actually want: investment range, industries you would and would not "
        "run, how hands-on you intend to be, where you want to live, and what return the deal has "
        "to produce for it to be worth doing.",
    ),
    (
        "Identifying the right opportunity",
        "Sourcing runs through the Business Brokers of Florida co-brokerage network, the national "
        "listing platforms, private broker relationships and direct owner and advisor contacts — "
        "which is where off-market opportunities come from.",
    ),
    (
        "Confidential review &amp; financial analysis",
        "Historical financials, business and excise tax returns, year-to-date performance, "
        "accounting files, contracts, leases and inventory. A structured review built to verify "
        "that the numbers in the listing are the numbers in the business.",
    ),
    (
        "Financing &amp; qualification",
        "Guidance through SBA lending and seller financing, including which businesses are already "
        "lender pre-qualified. You will sign an NDA and show financing capability before detailed "
        "information is released — the same standard applied to every buyer.",
    ),
    (
        "Offers, negotiation &amp; due diligence",
        "We structure the offer, negotiate terms and manage the diligence period so issues surface "
        "while you can still price them, rather than after you own them.",
    ),
    (
        "Closing &amp; transition",
        "Closing with experienced attorneys, then the handover. Sellers typically provide a "
        "transition period with initial training included; extended support can be arranged as a "
        "defined-term consulting agreement.",
    ),
]

# Business types Warren states he has sold, from his October 2025 OrlandoVoyager
# interview and his own Facebook page. First-person claims, not independently
# verified — see NOTES.md.
SOLD_TYPES = [
    "Medical facilities",
    "Restaurants",
    "Construction companies",
    "Cleaning services",
    "Dry cleaners &amp; laundry",
    "Property management firms",
    "Lawn &amp; landscaping",
    "Retail &amp; convenience",
]

# WBM B2B Business Consulting — non–real estate advisory services.
ADVISORY = [
    (
        "advice",
        "Exit strategy consulting",
        "Planning the exit before it is urgent: what the business needs to look like, what has to "
        "come off your plate, and how long it realistically takes to get there.",
    ),
    (
        "doc",
        "Proformas &amp; business planning",
        "Forward-looking financial models, business plans and budgets &mdash; for a lender, an "
        "investor, a partner buyout or your own decision-making.",
    ),
    (
        "chat",
        "Operations &amp; HR support",
        "Practical help with budgeting, staffing structure and the operating problems that depress "
        "the multiple a buyer is willing to pay.",
    ),
    (
        "badge",
        "E-2 visa business plans",
        "Business plans prepared for E-2 treaty investor visa applications, for buyers acquiring a "
        "U.S. business as part of a legal immigration route.",
    ),
]

FAQ_HOME = [
    (
        "What is my business worth?",
        "<p>It depends on your recast earnings, how transferable the business is without you, the "
        "quality of your records, your industry's multiple range and current buyer and lender "
        "appetite. A business doing $500,000 of owner benefit with clean books and a management "
        "team is worth materially more than one doing the same earnings out of a shoebox.</p>"
        "<p>The first conversation and the valuation discussion are confidential and come at no "
        "cost. You will get a realistic range and the reasoning behind it.</p>",
    ),
    (
        "How long does it take to sell a business?",
        "<p>Most Main Street and lower middle-market sales run six to twelve months from listing to "
        "closing. Preparation quality, price realism, record keeping and whether the deal needs SBA "
        "financing are the biggest variables. Businesses that go to market well prepared close "
        "faster and at better terms than those that go out quickly and get repriced later.</p>",
    ),
    (
        "How do you protect confidentiality?",
        "<p>Listings are marketed without identifying your business. Buyers receive general "
        "information first, and only sign-and-verify prospects — NDA executed plus proof of funds "
        "or financing capability — see financials, customer concentration, lease terms or your "
        "name. Employees, customers and competitors should learn about the sale from you, after it "
        "closes.</p>",
    ),
    (
        "Do you work with buyers as well as sellers?",
        "<p>Yes. Buyer representation is a significant part of the practice, including first-time "
        "buyers using SBA financing and operators making an add-on acquisition. If a conflict would "
        "arise on a specific transaction, it is disclosed up front.</p>",
    ),
    (
        "What does it cost?",
        "<p>Sell-side engagements work on a success fee at closing, agreed in writing before "
        "anything goes to market, with the term and any marketing costs stated plainly. There is "
        "no charge for the initial consultation or the valuation conversation.</p>",
    ),
    (
        "What areas of Florida do you cover?",
        "<p>Florida statewide, from the Orlando office. Activity is deepest across Central "
        "Florida &mdash; Orange, Seminole, Osceola, Lake and Brevard &mdash; and along the I-4 "
        "corridor and the Gulf Coast through Hillsborough, Pinellas, Pasco, Sarasota and Manatee, "
        "with transactions also on the Treasure Coast and in the Panhandle.</p>",
    ),
]

# --------------------------------------------------------------------------
# icons
# --------------------------------------------------------------------------

ICONS = {
    "doc": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M8 13h8M8 17h5"/>',
    "chat": '<path d="M21 11.5a8.4 8.4 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.4 8.4 0 0 1-3.8-.9L3 21l1.9-5.7a8.4 8.4 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.4 8.4 0 0 1 3.8-.9h.5a8.5 8.5 0 0 1 8 8z"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.3"/>',
    "sell": '<path d="M3 21h18"/><path d="M5 21V8l7-5 7 5v13"/><path d="M10 21v-6h4v6"/>',
    "buy": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.6-3.6"/><path d="M11 8v6M8 11h6"/>',
    "advice": '<path d="M12 3v2M12 19v2M5 12H3M21 12h-2M6.3 6.3 4.9 4.9M19.1 19.1l-1.4-1.4M6.3 17.7l-1.4 1.4M19.1 4.9l-1.4 1.4"/><circle cx="12" cy="12" r="4"/>',
    "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/>',
    "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m2 7 10 6 10-6"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0z"/><circle cx="12" cy="10" r="3"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>',
    "badge": '<circle cx="12" cy="9" r="6"/><path d="m8.5 14.5-1.5 7 5-3 5 3-1.5-7"/>',
}


def icon(name, cls="card__ico"):
    body = ICONS.get(name, "")
    return (
        f'<div class="{cls}"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg></div>'
    )


def inline_icon(name):
    body = ICONS.get(name, "")
    return (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
        f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{body}</svg>'
    )


ARROW = (
    '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M5 12h14M13 5l7 7-7 7"/></svg>'
)

SOC_SVG = {
    "linkedin": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M4.98 3.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5zM3 9h4v12H3zM9 9h3.8v1.7h.05A4.2 4.2 0 0 1 16.6 8.7c3 0 4.4 1.9 4.4 5.2V21h-4v-6c0-1.5-.5-2.5-1.9-2.5-1.1 0-1.8.8-2.1 1.5-.1.3-.1.7-.1 1V21H9z"/></svg>',
    "facebook": '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M22 12a10 10 0 1 0-11.6 9.9v-7H7.9V12h2.5V9.8c0-2.5 1.5-3.9 3.7-3.9 1.1 0 2.2.2 2.2.2v2.4h-1.2c-1.2 0-1.6.8-1.6 1.6V12h2.7l-.4 2.9h-2.3v7A10 10 0 0 0 22 12z"/></svg>',
}

# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


def fingerprint(path):
    with open(path, "rb") as fh:
        return hashlib.sha1(fh.read()).hexdigest()[:8]


def btn(href, label, kind="p", arrow=False):
    a = f" {ARROW}" if arrow else ""
    return f'<a class="btn btn--{kind}" href="{href}">{label}{a}</a>'


def tlink(href, label, external=False):
    ext = ' target="_blank" rel="noopener"' if external else ""
    return f'<a class="tlink" href="{href}"{ext}>{label} {ARROW}</a>'


def steps_html(steps):
    out = ['<div class="steps">']
    for title, body in steps:
        out.append(
            '<div class="step rv">'
            '<div class="step__n"></div>'
            f"<div><h3>{title}</h3><p>{body}</p></div>"
            "</div>"
        )
    out.append("</div>")
    return "".join(out)


def faq_html(items):
    out = ['<div class="faq">']
    for q, a in items:
        out.append(f"<details><summary>{q}</summary><div class=\"faq__a\">{a}</div></details>")
    out.append("</div>")
    return "".join(out)


def industries_html():
    out = ['<div class="inds">']
    for i, (name, desc) in enumerate(INDUSTRIES, 1):
        out.append(f'<div class="inds__i"><span>{i:02d}</span><div>{name}</div></div>')
    out.append("</div>")
    return "".join(out)


def contact_form(variant="general"):
    key = SITE["web3forms_key"]
    opts = {
        "general": [
            ("", "Select one"),
            ("selling", "I am thinking about selling a business"),
            ("buying", "I am looking to buy a business"),
            ("valuation", "I want a confidential valuation"),
            ("advisory", "Business consulting / advisory"),
            ("other", "Something else"),
        ],
    }["general"]
    sel = "".join(f'<option value="{v}">{t}</option>' for v, t in opts)

    return f"""
<form class="form" data-form data-key="{key}" novalidate>
  <input type="hidden" name="form_name" value="wim_contact_{variant}">
  <input type="checkbox" name="botcheck" class="hp" tabindex="-1" aria-hidden="true">
  <div class="form__row">
    <div class="fld">
      <label for="f-first">First name <span class="req">*</span></label>
      <input id="f-first" name="first_name" type="text" autocomplete="given-name" required>
      <div class="fld__err" aria-live="polite"></div>
    </div>
    <div class="fld">
      <label for="f-last">Last name <span class="req">*</span></label>
      <input id="f-last" name="last_name" type="text" autocomplete="family-name" required>
      <div class="fld__err" aria-live="polite"></div>
    </div>
  </div>
  <div class="form__row">
    <div class="fld">
      <label for="f-email">Email <span class="req">*</span></label>
      <input id="f-email" name="email" type="email" autocomplete="email" required>
      <div class="fld__err" aria-live="polite"></div>
    </div>
    <div class="fld">
      <label for="f-phone">Phone <span class="req">*</span></label>
      <input id="f-phone" name="phone" type="tel" autocomplete="tel" inputmode="tel" required>
      <div class="fld__err" aria-live="polite"></div>
    </div>
  </div>
  <div class="form__row">
    <div class="fld">
      <label for="f-intent">How can Warren help? <span class="req">*</span></label>
      <select id="f-intent" name="intent" required>{sel}</select>
      <div class="fld__err" aria-live="polite"></div>
    </div>
    <div class="fld">
      <label for="f-industry">Industry / type of business</label>
      <input id="f-industry" name="industry" type="text" placeholder="e.g. HVAC contractor, CPA practice">
      <div class="fld__err" aria-live="polite"></div>
    </div>
  </div>
  <div class="form__row">
    <div class="fld">
      <label for="f-range">Price or budget range</label>
      <input id="f-range" name="price_range" type="text" placeholder="e.g. $500K &ndash; $2M">
      <div class="fld__err" aria-live="polite"></div>
    </div>
    <div class="fld">
      <label for="f-timeline">Timeline</label>
      <input id="f-timeline" name="timeline" type="text" placeholder="e.g. next 6 months">
      <div class="fld__err" aria-live="polite"></div>
    </div>
  </div>
  <div class="fld">
    <label for="f-msg">Anything you would like to add</label>
    <textarea id="f-msg" name="message" placeholder="A few sentences is plenty. Everything you send is treated as confidential."></textarea>
    <div class="fld__err" aria-live="polite"></div>
  </div>
  <div class="fld">
    <label class="form__consent" for="f-terms">
      <input id="f-terms" name="terms_and_privacy_accepted" type="checkbox" value="yes" required>
      <span>I have read and agree to the <a href="/privacy">Privacy Policy</a> and
      <a href="/terms">Terms of Service</a>. <span class="req">*</span></span>
    </label>
    <div class="fld__err" aria-live="polite"></div>
  </div>
  <div>
    <button class="btn btn--p" type="submit">Send confidential inquiry</button>
  </div>
  <div class="form__status" role="status" aria-live="polite"></div>
  <p class="form__note">
    Your information is used only to respond to your inquiry. It is never sold or shared with third
    parties for marketing. Prefer to talk first? Call or text
    <a href="tel:{SITE['tel_href']}">{SITE['tel_display']}</a>.
  </p>
</form>
"""


# --------------------------------------------------------------------------
# structured data
# --------------------------------------------------------------------------


def jsonld_org():
    data = {
        "@context": "https://schema.org",
        "@type": ["RealEstateAgent", "ProfessionalService"],
        "@id": SITE["base"] + "/#org",
        "name": SITE["name"],
        "alternateName": [SITE["dba"], "WIM Services"],
        "description": (
            "Florida business brokerage and M&A advisory for Main Street and lower "
            "middle-market companies. Business sales, acquisitions and confidential valuations."
        ),
        "url": SITE["base"] + "/",
        "telephone": "+1-360-904-4060",
        "email": SITE["email"],
        "areaServed": {"@type": "State", "name": "Florida"},
        "founder": {"@type": "Person", "@id": SITE["base"] + "/about#warren"},
        "slogan": SITE["tagline"],
        "knowsAbout": [
            "Business brokerage",
            "Mergers and acquisitions",
            "Business valuation",
            "SBA acquisition financing",
            "Exit planning",
            "Florida liquor licenses",
        ],
        "address": [
            {
                "@type": "PostalAddress",
                "streetAddress": o["street"],
                "addressLocality": o["locality"],
                "addressRegion": o["region"],
                "postalCode": o["zip"],
                "addressCountry": "US",
            }
            for o in SITE["offices"]
        ],
        "sameAs": [
            SITE["social"]["linkedin"],
            SITE["social"]["facebook"],
            SITE["social"]["bizbuysell"],
            SITE["social"]["bizquest"],
        ],
    }
    return json.dumps(data, separators=(",", ":"))


def jsonld_person():
    data = {
        "@context": "https://schema.org",
        "@type": "Person",
        "@id": SITE["base"] + "/about#warren",
        "name": SITE["person"],
        "givenName": "Warren",
        "familyName": "Merrill",
        "jobTitle": "Business Broker",
        "telephone": "+1-360-904-4060",
        "email": SITE["email"],
        "worksFor": {"@id": SITE["base"] + "/#org"},
        "url": SITE["base"] + "/about",
        "hasCredential": [
            {
                "@type": "EducationalOccupationalCredential",
                "credentialCategory": "license",
                "name": f"Florida Licensed Real Estate Broker {SITE['broker_lic']}",
            },
            {
                "@type": "EducationalOccupationalCredential",
                "credentialCategory": "license",
                "name": f"Florida Licensed Real Estate Brokerage {SITE['brokerage_lic']}",
            },
        ],
        "memberOf": [
            {"@type": "Organization", "name": "Business Brokers of Florida"},
            {"@type": "Organization", "name": "International Business Brokers Association"},
        ],
        "sameAs": [SITE["social"]["linkedin"], SITE["social"]["facebook"]],
    }
    return json.dumps(data, separators=(",", ":"))


def jsonld_faq(items):
    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": re.sub(r"<[^>]+>", "", q),
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", a)).strip(),
                },
            }
            for q, a in items
        ],
    }
    return json.dumps(data, separators=(",", ":"))


def jsonld_breadcrumb(slug, title):
    data = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE["base"] + "/"},
            {
                "@type": "ListItem",
                "position": 2,
                "name": re.sub(r"<[^>]+>", "", title),
                "item": SITE["base"] + "/" + slug,
            },
        ],
    }
    return json.dumps(data, separators=(",", ":"))


def jsonld_service(name, desc, slug):
    data = {
        "@context": "https://schema.org",
        "@type": "Service",
        "name": name,
        "description": desc,
        "serviceType": name,
        "provider": {"@id": SITE["base"] + "/#org"},
        "areaServed": {"@type": "State", "name": "Florida"},
        "url": SITE["base"] + "/" + slug,
    }
    return json.dumps(data, separators=(",", ":"))


# --------------------------------------------------------------------------
# chrome
# --------------------------------------------------------------------------


def header(active):
    nav = "".join(
        f'<a href="{href}"{" aria-current=\"page\"" if href.lstrip("/") == active else ""}>{label}</a>'
        for href, label in NAV
    )
    mnav = "".join(f'<a href="{href}">{label}</a>' for href, label in NAV)
    return f"""<a class="skip" href="#main">Skip to content</a>
<header class="hdr">
  <div class="wrap hdr__bar">
    <a class="brand" href="/" aria-label="{SITE['name']} home">
      <span class="brand__mark" aria-hidden="true">W</span>
      <span class="brand__txt">
        <span class="brand__name">WIM Services</span>
        <span class="brand__sub">Business Sales &middot; M&amp;A</span>
      </span>
    </a>
    <nav class="nav" aria-label="Main">{nav}</nav>
    <div class="hdr__cta">
      <a class="hdr__tel" href="tel:{SITE['tel_href']}">{SITE['tel_display']}</a>
      {btn('/contact', 'Confidential consultation', 'p')}
      <button class="burger" type="button" aria-expanded="false" aria-controls="mnav" aria-label="Menu">
        <span></span><span></span><span></span>
      </button>
    </div>
  </div>
  <div class="mnav" id="mnav">
    {mnav}
    <a href="tel:{SITE['tel_href']}">Call or text {SITE['tel_display']}</a>
    {btn('/contact', 'Confidential consultation', 'p')}
  </div>
</header>"""


def band(title, body, primary=("/contact", "Start a confidential conversation"), secondary=None):
    sec = btn(secondary[0], secondary[1], "o") if secondary else ""
    return f"""<section class="band">
  <div class="wrap band__inner rv">
    <p class="eyebrow eyebrow--c">Next step</p>
    <h2>{title}</h2>
    <p class="lede" style="margin:0 auto">{body}</p>
    <div class="btn-row btn-row--c">{btn(primary[0], primary[1], 'p')}{sec}</div>
  </div>
</section>"""


def footer():
    offices = "".join(
        f'<li>{o["street"]}<br>{o["locality"]}, {o["region"]} {o["zip"]}</li>'
        for o in SITE["offices"]
    )
    serve = "".join(f'<li><a href="/industries">{n.replace("&amp;", "&")}</a></li>' for n, _ in INDUSTRIES[:5])
    return f"""<footer class="ftr">
  <div class="wrap">
    <div class="ftr__top">
      <div>
        <span class="brand__name" style="font-size:1.25rem">WIM Services, LLC</span>
        <p class="ftr__tag">&ldquo;{SITE['tagline']}&rdquo;</p>
        <div class="ftr__soc">
          <a href="{SITE['social']['linkedin']}" target="_blank" rel="noopener" aria-label="LinkedIn">{SOC_SVG['linkedin']}</a>
          <a href="{SITE['social']['facebook']}" target="_blank" rel="noopener" aria-label="Facebook">{SOC_SVG['facebook']}</a>
        </div>
      </div>
      <div>
        <h4>Services</h4>
        <ul>
          <li><a href="/selling-a-business">Selling a business</a></li>
          <li><a href="/buying-a-business">Buying a business</a></li>
          <li><a href="/listings">Businesses for sale</a></li>
          <li><a href="/industries">Industries served</a></li>
          <li><a href="/contact">Confidential valuation</a></li>
        </ul>
      </div>
      <div>
        <h4>Focus areas</h4>
        <ul>{serve}</ul>
      </div>
      <div>
        <h4>Contact</h4>
        <ul>
          <li><a href="tel:{SITE['tel_href']}">Call or text {SITE['tel_display']}</a></li>
          <li><a href="mailto:{SITE['email']}">{SITE['email']}</a></li>
          {offices}
        </ul>
      </div>
    </div>
    <p class="ftr__lic">
      {SITE['name']} ({SITE['brokerage_lic']}) is a licensed Florida real estate brokerage.
      {SITE['person']}, General Manager and Business Broker, Florida Licensed Real Estate Broker
      {SITE['broker_lic']}. Also licensed in Florida as a Community Association Manager
      ({SITE['cam_lic']}); {SITE['name']} is a licensed CAM firm ({SITE['cab_lic']}).
      WBM B2B Business Consulting provides business advisory services;
      business consulting is a non&ndash;real estate service and is not offered under the brokerage
      license. Member, Business Brokers of Florida. Member, International Business Brokers
      Association. Information on this site is provided for general information only and is not
      legal, tax, accounting or investment advice. Business listings and financial information are
      supplied by owners and are not independently verified unless expressly stated.
    </p>
    <div class="ftr__legal">
      <span>&copy; {YEAR} {SITE['name']}. All rights reserved.</span>
      <nav aria-label="Legal">
        <a href="/privacy">Privacy Policy</a>
        <a href="/terms">Terms of Service</a>
        <a href="/contact">Contact</a>
      </nav>
    </div>
  </div>
</footer>"""


def ga_snippet():
    gid = SITE["ga4_id"]
    if not gid:
        return ""
    return f"""<script async src="https://www.googletagmanager.com/gtag/js?id={gid}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}
gtag('js',new Date());gtag('config','{gid}');</script>"""


# --------------------------------------------------------------------------
# page shell
# --------------------------------------------------------------------------


def page(slug, title, desc, body, schemas=(), noindex=False, css_v="", js_v=""):
    canonical = SITE["base"] + "/" + ("" if slug == "index" else slug)
    full_title = title if slug == "index" else f"{title} | WIM Services, LLC"
    robots = (
        '<meta name="robots" content="noindex,nofollow,noarchive">'
        if noindex
        else '<meta name="robots" content="index,follow,max-image-preview:large">'
    )
    schema_tags = "".join(
        f'<script type="application/ld+json">{s}</script>' for s in schemas
    )
    active = "" if slug == "index" else slug
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{full_title}</title>
<meta name="description" content="{desc}">
{robots}
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{SITE['name']}">
<meta property="og:title" content="{full_title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#0C1722">
<link rel="preload" href="/fonts/newsreader-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/fonts/inter-wght-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/fonts/fonts.css?v={css_v}">
<link rel="stylesheet" href="/css/site.css?v={css_v}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
{schema_tags}
{ga_snippet()}
</head>
<body>
{header(active)}
<main id="main">
{body}
</main>
{footer()}
<script src="/js/site.js?v={js_v}" defer></script>
</body>
</html>
"""


# --------------------------------------------------------------------------
# pages
# --------------------------------------------------------------------------


def home():
    cards = ""
    for ic, t, b in PRINCIPLES:
        cards += f'<div class="card card--flat rv">{icon(ic)}<h3>{t}</h3><p>{b}</p></div>'

    paths = f"""<div class="grid g2">
  <div class="card rv">
    {icon('sell')}
    <h3>Selling a business</h3>
    <p>A structured, confidential process from valuation through closing &mdash; built so your
    employees, customers and competitors do not find out before you are ready.</p>
    {tlink('/selling-a-business', 'How a sale works')}
  </div>
  <div class="card rv">
    {icon('buy')}
    <h3>Buying a business</h3>
    <p>Access to the Business Brokers of Florida network, national platforms and off-market
    opportunities, with help through SBA lending and seller financing.</p>
    {tlink('/buying-a-business', 'How an acquisition works')}
  </div>
</div>"""

    body = f"""
<section class="hero">
  <div class="wrap hero__inner">
    <p class="eyebrow">Florida Business Brokerage &amp; M&amp;A Advisory</p>
    <h1>Buy or sell a Florida business &mdash; guided by an owner, <em>not just a broker.</em></h1>
    <div class="hero__rule"></div>
    <p class="hero__lede">{SITE['person']} has built, operated and sold fourteen of his own
    companies across more than thirty years. He brings an operator's judgement to every Main
    Street and lower middle-market transaction in Florida.</p>
    <div class="btn-row">
      {btn('/contact', 'Request a confidential valuation', 'p')}
      {btn('/listings', 'Browse businesses for sale', 'o')}
    </div>
    <div class="stats">
      <div><span class="stat__n" data-count="14">14</span><span class="stat__l">Businesses built, bought &amp; sold</span></div>
      <div><span class="stat__n" data-count="30" data-suffix="+">30+</span><span class="stat__l">Years of experience</span></div>
      <div><span class="stat__n" data-count="10">10</span><span class="stat__l">Industry sectors served</span></div>
      <div><span class="stat__n">FL</span><span class="stat__l">Statewide coverage</span></div>
    </div>
  </div>
</section>

<section class="ribbon">
  <div class="wrap ribbon__row">
    <span class="ribbon__i">{inline_icon('badge')} FL Licensed Real Estate Broker {SITE['broker_lic']}</span>
    <span class="ribbon__i">{inline_icon('shield')} Business Brokers of Florida</span>
    <span class="ribbon__i">{inline_icon('badge')} IBBA Member since 2021</span>
    <span class="ribbon__i">{inline_icon('shield')} Deals from $50K to $3M+</span>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="grid split">
      <div class="rv">
        <p class="eyebrow">The difference</p>
        <h2>He has sat on your side of the table.</h2>
      </div>
      <div class="rv">
        <p class="lede">Most brokers have sold businesses. Warren has <em>owned</em> them &mdash;
        fourteen companies in construction, convenience retail, manufacturing, professional
        services, real estate, restaurants, retail and field services, each built hands-on and
        exited profitably.</p>
        <p>That matters in the moments a transaction actually turns: when a buyer's lender
        re-trades the deal, when a lease assignment stalls, when diligence surfaces something
        awkward in the books, or when a seller has to decide whether a number is worth the terms
        attached to it. Those are operator judgements, not paperwork.</p>
        {tlink('/about', 'More about Warren')}
      </div>
    </div>
  </div>
</section>

<section class="sec--tight">
  <div class="wrap">
    <blockquote class="pq rv">
      {SITE['tagline']}
      <cite>{SITE['person']} &mdash; {SITE['role']}</cite>
    </blockquote>
  </div>
</section>

<section class="sec dark">
  <div class="wrap">
    <div style="max-width:60ch;margin-bottom:clamp(2.5rem,5vw,4rem)" class="rv">
      <p class="eyebrow">How the practice works</p>
      <h2>Three principles, applied to every engagement.</h2>
    </div>
    <div class="grid g3">{cards}</div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div style="max-width:62ch;margin-bottom:clamp(2.5rem,5vw,3.5rem)" class="rv">
      <p class="eyebrow">Two sides of the table</p>
      <h2>Whether you are exiting or acquiring.</h2>
    </div>
    {paths}
  </div>
</section>

<section class="sec" style="padding-top:0">
  <div class="wrap">
    <div class="grid split">
      <div class="rv">
        <p class="eyebrow">Industries</p>
        <h2>Where the deal experience is deepest.</h2>
        <p class="lede" style="margin-top:1.4rem">Main Street and lower middle-market companies,
        typically with $1M or more in revenue, plus restaurant and Florida quota liquor license
        transactions in Central and South Florida.</p>
        <div class="btn-row">{btn('/industries', 'Industries served', 'o', True)}</div>
      </div>
      <div class="rv">{industries_html()}</div>
    </div>
  </div>
</section>

<section class="sec" style="padding-top:0">
  <div class="wrap">
    <div class="grid split">
      <div class="rv">
        <p class="eyebrow">Track record</p>
        <h2>The kinds of businesses that have changed hands.</h2>
        <p class="lede" style="margin-top:1.4rem">Transactions have ranged from roughly $50,000 to
        over $3 million &mdash; service, manufacturing, retail and medical businesses, taken from
        the asset purchase agreement through SBA lending to the closing attorney.</p>
      </div>
      <div class="rv">
        <ul class="checks checks--2">{"".join(f"<li>{t}</li>" for t in SOLD_TYPES)}</ul>
        <div class="btn-row">{tlink('/about', "Warren's background")}</div>
      </div>
    </div>
  </div>
</section>

<section class="sec dark">
  <div class="wrap wrap--narrow">
    <div class="tc rv" style="margin-bottom:clamp(2.5rem,5vw,3.5rem)">
      <p class="eyebrow eyebrow--c">Timeline</p>
      <h2>Most sales take six to twelve months.</h2>
      <p class="lede" style="margin:1.4rem auto 0">Preparation quality, price realism and whether
      the deal needs SBA financing drive most of that range. Here is the shape of it.</p>
    </div>
    {steps_html([(t, b) for t, b in [
      ("Confidential valuation", "A candid conversation about where your business realistically sits in the market, and what would move it."),
      ("Preparation &amp; packaging", "Recast financials, a confidential information memorandum and a listing a buyer and a lender can both underwrite."),
      ("Marketing &amp; buyer vetting", "Targeted, discreet exposure. NDA-protected information released only to screened, financially capable prospects."),
      ("Negotiation &amp; closing", "Offer evaluation, deal structuring, diligence support and closing coordinated with experienced attorneys."),
    ]])}
    <div class="btn-row btn-row--c">{btn('/selling-a-business', 'The full seller process', 'g', True)}</div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div style="max-width:62ch;margin-bottom:clamp(2.5rem,5vw,3.5rem)" class="rv">
      <p class="eyebrow">Beyond the transaction</p>
      <h2>WBM B2B Business Consulting.</h2>
      <p class="lede" style="margin-top:1.4rem">Not every owner is ready to sell, and not every
      problem is a transaction. Advisory engagements are offered separately from the brokerage as
      non&ndash;real estate services.</p>
    </div>
    <div class="grid g4">{"".join(f'<div class="card card--flat rv">{icon(ic)}<h3 style="font-size:1.15rem">{t}</h3><p>{b}</p></div>' for ic, t, b in ADVISORY)}</div>
    <div class="btn-row">{btn('/contact', 'Discuss an advisory engagement', 'o', True)}</div>
  </div>
</section>

<section class="sec" style="padding-top:0">
  <div class="wrap wrap--narrow">
    <div class="rv" style="margin-bottom:2.5rem">
      <p class="eyebrow">Common questions</p>
      <h2>What owners and buyers ask first.</h2>
    </div>
    {faq_html(FAQ_HOME)}
  </div>
</section>

{band(
  "Start with a confidential conversation.",
  "No cost, no obligation, and nothing leaves the room. Whether you are twelve months from "
  "an exit or just want to know what your business is worth, that is a good place to begin.",
  ("/contact", "Request a confidential consultation"),
  ("tel:" + SITE["tel_href"], "Call or text " + SITE["tel_display"]),
)}
"""
    return page(
        "index",
        "Florida Business Broker | Buy or Sell a Business | WIM Services, LLC",
        "Florida business brokerage and M&A advisory for Main Street and lower middle-market "
        "companies. Warren B. Merrill has built, bought and sold 14 of his own businesses. "
        "Confidential valuations, business sales and acquisitions statewide.",
        body,
        schemas=(jsonld_org(), jsonld_person(), jsonld_faq(FAQ_HOME)),
    )


def selling():
    faqs = [
        (
            "What do you need from me to start?",
            "<p>Roughly three years of financial statements and tax returns, current year-to-date "
            "results, a copy of your lease, and an hour of conversation. That is enough to give you "
            "a realistic valuation range and tell you honestly whether now is the right time.</p>",
        ),
        (
            "Will my employees or customers find out?",
            "<p>Not from us. Your business is marketed on a blind basis without its name, and "
            "identifying details are released only after a buyer signs an NDA and demonstrates "
            "financial capability. Protecting the business while it is for sale is part of the job, "
            "not an add-on.</p>",
        ),
        (
            "What if my books are not clean?",
            "<p>Very common, and fixable &mdash; but better fixed before going to market than "
            "discovered in diligence. Recasting owner benefit, separating personal expenses and "
            "reconciling the accounting file are part of preparation. If the gap is large enough to "
            "affect value, the honest answer may be to spend a year tidying up first.</p>",
        ),
        (
            "Do I have to stay on after closing?",
            "<p>Usually a short transition with training included in the sale. Many buyers want "
            "more, and that can be structured as a defined-term consulting agreement with the "
            "compensation set in the overall deal. What you do not want is an open-ended obligation "
            "agreed casually at closing.</p>",
        ),
        (
            "Can the buyer get SBA financing?",
            "<p>Often, and it widens your buyer pool considerably. SBA lenders look at transferable "
            "cash flow, clean records, customer concentration, lease term and the collateral "
            "position. Businesses that can be pre-qualified by a lender before listing tend to "
            "attract more serious interest.</p>",
        ),
    ]
    body = f"""
<section class="phero">
  <div class="wrap">
    <p class="crumbs"><a href="/">Home</a><span>/</span>Selling a business</p>
    <h1>Sell your business with confidence.</h1>
    <p class="lede">Selling is a financial decision and a personal one. The process below is built
    to protect the business while it is on the market and to get you to a closing that actually
    funds.</p>
    <div class="btn-row">
      {btn('/contact', 'Request a confidential valuation', 'g')}
      {btn('tel:' + SITE['tel_href'], 'Call or text ' + SITE['tel_display'], 'o')}
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="grid split">
      <div class="rv">
        <p class="eyebrow">Before you list</p>
        <h2>The preparation decides the outcome.</h2>
      </div>
      <div class="rv">
        <p class="lede">Most businesses that sit unsold for a year were not priced wrong so much as
        prepared poorly &mdash; or priced on a number nobody could substantiate.</p>
        <p>The work that happens before a listing goes live is what a buyer's lender underwrites
        and what a buyer's accountant tests in diligence. Recast earnings that hold up. Records that
        reconcile. A lease with term left on it. A business that can run without you in the building
        every day. Each of those moves the price, and all of them are easier to fix before a buyer
        is watching.</p>
        <ul class="checks">
          <li>Recast owner benefit and normalised earnings a lender will accept</li>
          <li>Three years of financials reconciled to the tax returns</li>
          <li>Customer concentration and key-person risk identified and addressed</li>
          <li>Lease term, assignability and landlord consent confirmed early</li>
          <li>Licences, permits and any transfer conditions mapped out</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="sec dark">
  <div class="wrap">
    <div style="max-width:60ch;margin-bottom:clamp(2.5rem,5vw,3.5rem)" class="rv">
      <p class="eyebrow">The process</p>
      <h2>Five stages, start to closing.</h2>
      <p class="lede" style="margin-top:1.4rem">Typically six to twelve months. You will know which
      stage you are in and what is next at every point.</p>
    </div>
    {steps_html(SELL_STEPS)}
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="grid split">
      <div class="rv">
        <p class="eyebrow">Confidentiality</p>
        <h2>The sale should be news only after it closes.</h2>
      </div>
      <div class="rv">
        <p>A leak costs real money. Key employees start looking, your best customers ask
        uncomfortable questions, suppliers tighten terms and competitors go recruiting. Every
        marketing decision is made with that risk in front of it.</p>
        <ul class="checks">
          <li>Blind listings &mdash; no business name, no identifying photographs</li>
          <li>Non-disclosure agreement executed before any detail is released</li>
          <li>Proof of funds or demonstrated financing capability before financials</li>
          <li>Buyer screening for seriousness, not just curiosity</li>
          <li>Site visits scheduled so they do not disrupt the business</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="sec" style="padding-top:0">
  <div class="wrap wrap--narrow">
    <div class="rv" style="margin-bottom:2.5rem">
      <p class="eyebrow">Seller questions</p>
      <h2>What owners ask before they commit.</h2>
    </div>
    {faq_html(faqs)}
  </div>
</section>

{band(
  "What is your business worth?",
  "The valuation conversation is confidential and comes at no cost. You will get a realistic "
  "range, the reasoning behind it, and a straight answer about timing.",
  ("/contact", "Request a confidential valuation"),
  ("/buying-a-business", "Buying instead?"),
)}
"""
    return page(
        "selling-a-business",
        "Selling a Business in Florida",
        "Sell your Florida business confidentially. Valuation, recast financials, discreet "
        "buyer-vetted marketing and closing support from a broker who has sold 14 of his own "
        "companies. Typically six to twelve months.",
        body,
        schemas=(
            jsonld_service(
                "Business sale representation",
                "Sell-side business brokerage for Florida Main Street and lower middle-market "
                "companies: valuation, confidential marketing, buyer qualification, negotiation "
                "and closing coordination.",
                "selling-a-business",
            ),
            jsonld_breadcrumb("selling-a-business", "Selling a business"),
            jsonld_faq(faqs),
        ),
    )


def buying():
    faqs = [
        (
            "How much cash do I need?",
            "<p>With SBA acquisition financing, buyers commonly put down a meaningful share of the "
            "purchase price, with the balance financed and sometimes a seller note filling part of "
            "the gap. You also need working capital after closing and reserves &mdash; the mistake "
            "first-time buyers make most often is spending every dollar on the down payment. Your "
            "lender will set the specifics; we will tell you early whether a deal is realistic.</p>",
        ),
        (
            "What is a lender pre-qualified listing?",
            "<p>A business an SBA lender has already reviewed and indicated it would finance, "
            "subject to the buyer qualifying. It removes much of the uncertainty about whether the "
            "deal can be funded at all, which is the most common reason acquisitions die.</p>",
        ),
        (
            "Can I see off-market businesses?",
            "<p>Sometimes. Sourcing runs through the Business Brokers of Florida co-brokerage "
            "network, the national listing platforms, private broker relationships and direct owner "
            "and advisor contacts. Owners who are quietly open to an offer but not formally listed "
            "come through the last of those.</p>",
        ),
        (
            "What should I actually check in due diligence?",
            "<p>That the earnings are real and transferable. Financial statements reconciled to tax "
            "returns, bank deposits against reported revenue, customer concentration, the accounting "
            "file itself, contracts and their assignability, the lease, employee agreements, "
            "licences, inventory condition and any pending liabilities. We coordinate a structured "
            "review rather than a checklist skim.</p>",
        ),
        (
            "Do I pay you as a buyer?",
            "<p>In most transactions the seller pays the brokerage fee, including on co-brokered "
            "deals. Where a buy-side engagement is fee-bearing, that is agreed in writing before "
            "any work begins &mdash; never discovered later.</p>",
        ),
    ]
    body = f"""
<section class="phero">
  <div class="wrap">
    <p class="crumbs"><a href="/">Home</a><span>/</span>Buying a business</p>
    <h1>Buy a business with confidence.</h1>
    <p class="lede">Buying an established company is a large decision made on imperfect
    information. The job is to narrow the field to opportunities that fit your goals, then verify
    that the business performs the way the listing says it does.</p>
    <div class="btn-row">
      {btn('/listings', 'Browse businesses for sale', 'g')}
      {btn('/contact', 'Tell Warren what you are looking for', 'o')}
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="grid split">
      <div class="rv">
        <p class="eyebrow">Start here</p>
        <h2>The right business is a fit question before it is a price question.</h2>
      </div>
      <div class="rv">
        <p class="lede">A profitable business you are not suited to run is a bad acquisition at
        any multiple.</p>
        <p>So the first conversation is about you: the capital you can deploy and still sleep, the
        industries you would genuinely run, whether you intend to operate day-to-day or hire a
        manager, where you want to be based, and what the deal has to return to justify leaving
        whatever you are doing now. Screening against that saves months of looking at the wrong
        companies.</p>
        <ul class="checks checks--2">
          <li>Investment range and financing route</li>
          <li>Industries in and out of scope</li>
          <li>Operating involvement</li>
          <li>Geography within Florida</li>
          <li>Required return and risk tolerance</li>
          <li>Timeline to close</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="sec dark">
  <div class="wrap">
    <div style="max-width:60ch;margin-bottom:clamp(2.5rem,5vw,3.5rem)" class="rv">
      <p class="eyebrow">The process</p>
      <h2>Six stages, search to closing.</h2>
    </div>
    {steps_html(BUY_STEPS)}
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div style="max-width:62ch;margin-bottom:clamp(2.5rem,5vw,3.5rem)" class="rv">
      <p class="eyebrow">Financing</p>
      <h2>How acquisitions actually get funded.</h2>
    </div>
    <div class="grid g3">
      <div class="card card--flat rv">
        {icon('badge')}
        <h3>SBA acquisition loans</h3>
        <p>The most common route for Main Street deals. Lenders underwrite transferable cash flow,
        record quality, customer concentration, lease term and collateral. Some listings are
        pre-qualified by a lender before they reach the market.</p>
      </div>
      <div class="card card--flat rv">
        {icon('doc')}
        <h3>Seller financing</h3>
        <p>A seller note can bridge a valuation gap, satisfy a lender's equity requirement and keep
        the previous owner invested in a clean transition. Terms, security and any offset rights
        matter as much as the rate.</p>
      </div>
      <div class="card card--flat rv">
        {icon('clock')}
        <h3>Transition &amp; training</h3>
        <p>Sellers typically include an initial training period in the sale. Extended help can be
        arranged as a defined-term consulting agreement, with compensation set inside the overall
        agreement rather than negotiated after closing.</p>
      </div>
    </div>
  </div>
</section>

<section class="sec" style="padding-top:0">
  <div class="wrap wrap--narrow">
    <div class="rv" style="margin-bottom:2.5rem">
      <p class="eyebrow">Buyer questions</p>
      <h2>What buyers ask first.</h2>
    </div>
    {faq_html(faqs)}
  </div>
</section>

{band(
  "Tell Warren what you are looking for.",
  "A short conversation about your range, your industries and your timeline is enough to start "
  "surfacing opportunities that actually fit &mdash; including ones not publicly listed.",
  ("/contact", "Start a buyer conversation"),
  ("/listings", "See current listings"),
)}
"""
    return page(
        "buying-a-business",
        "Buying a Business in Florida",
        "Buy an established Florida business with guidance through sourcing, due diligence, SBA "
        "financing and closing. Access to the Business Brokers of Florida network, national "
        "platforms and off-market opportunities.",
        body,
        schemas=(
            jsonld_service(
                "Business acquisition representation",
                "Buy-side business brokerage in Florida: opportunity sourcing, financial review, "
                "SBA and seller financing guidance, due diligence coordination and closing.",
                "buying-a-business",
            ),
            jsonld_breadcrumb("buying-a-business", "Buying a business"),
            jsonld_faq(faqs),
        ),
    )


def industries():
    blocks = ""
    for i, (name, desc) in enumerate(INDUSTRIES, 1):
        blocks += (
            '<div class="card card--flat rv">'
            f'<div class="step__n" style="min-width:0;padding:0;margin-bottom:.9rem">{i:02d}</div>'
            f"<h3>{name}</h3><p>{desc}</p></div>"
        )
    body = f"""
<section class="phero">
  <div class="wrap">
    <p class="crumbs"><a href="/">Home</a><span>/</span>Industries</p>
    <h1>Industries served.</h1>
    <p class="lede">Main Street and lower middle-market companies across Florida, with the deepest
    transaction experience in the sectors Warren has owned and operated in himself.</p>
    <div class="btn-row">{btn('/contact', 'Discuss your business', 'g')}</div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="grid split">
      <div class="rv">
        <p class="eyebrow">Focus</p>
        <h2>Owned, operated, then sold.</h2>
      </div>
      <div class="rv">
        <p class="lede">Warren's own fourteen companies spanned construction, convenience retail,
        manufacturing, professional services, real estate, restaurants, retail and service
        businesses &mdash; each built hands-on and exited profitably.</p>
        <p>That is why the sector list below is not a marketing menu. It reflects where he has
        run payroll, chased receivables, managed a crew, dealt with a landlord and signed the
        personal guarantee &mdash; and where, as a broker, he has represented owners and buyers
        through the same transactions since.</p>
      </div>
    </div>
  </div>
</section>

<section class="sec dark" style="padding-top:0;background:var(--ink)">
  <div class="wrap" style="padding-top:var(--sec)">
    <div style="max-width:60ch;margin-bottom:clamp(2.5rem,5vw,3.5rem)" class="rv">
      <p class="eyebrow">Sectors</p>
      <h2>Ten sectors, one standard of preparation.</h2>
    </div>
    <div class="grid g3">{blocks}</div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="grid g3">
      <div class="card rv">
        {icon('shield')}
        <h3>High-revenue businesses</h3>
        <p>Companies typically at $1M or more in revenue, where buyer sophistication, lender
        requirements and deal structure all step up a level.</p>
      </div>
      <div class="card rv">
        {icon('badge')}
        <h3>Restaurants &amp; liquor licenses</h3>
        <p>Independent restaurants, bars and Florida quota liquor licenses, concentrated in
        Central and South Florida where the transfer market is most active.</p>
      </div>
      <div class="card rv">
        {icon('doc')}
        <h3>SBA pre-qualified listings</h3>
        <p>Businesses reviewed by a lender before going to market, so buyers know the deal can be
        financed and sellers reach a wider pool.</p>
      </div>
    </div>
  </div>
</section>

<section class="sec" style="padding-top:0">
  <div class="wrap">
    <div class="grid split">
      <div class="rv">
        <p class="eyebrow">Coverage</p>
        <h2>Florida statewide, run from Orlando.</h2>
        <p class="lede" style="margin-top:1.4rem">Activity is deepest across Central Florida and
        along the I-4 corridor and Gulf Coast &mdash; with closed transactions from Sarasota and
        Manatee up through the Panhandle.</p>
      </div>
      <div class="rv">
        <dl class="ctiles">
          <div class="ctile">
            <div class="ctile__ico">{inline_icon('pin')}</div>
            <div>
              <dt>Office</dt>
              <dd>{SITE['offices'][0]['street']}<br>{SITE['offices'][0]['locality']}, {SITE['offices'][0]['region']} {SITE['offices'][0]['zip']}</dd>
            </div>
          </div>
          <div class="ctile">
            <div class="ctile__ico">{inline_icon('pin')}</div>
            <div>
              <dt>Core counties</dt>
              <dd>Orange, Seminole, Osceola, Lake and Brevard, plus Hillsborough, Pinellas, Pasco,
              Sarasota and Manatee on the Gulf Coast.</dd>
            </div>
          </div>
          <div class="ctile">
            <div class="ctile__ico">{inline_icon('clock')}</div>
            <div>
              <dt>Deal size</dt>
              <dd>Transactions from roughly $50,000 to over $3 million.</dd>
            </div>
          </div>
        </dl>
      </div>
    </div>
  </div>
</section>

{band(
  "Does your business fit?",
  "If your company is in one of these sectors &mdash; or close to it &mdash; a confidential "
  "conversation will tell you quickly where it sits in today's market.",
)}
"""
    return page(
        "industries",
        "Industries Served | Florida Business Broker",
        "Florida business brokerage across business and professional services, construction, "
        "manufacturing and wholesale, restaurants and liquor licenses, health care, logistics, "
        "finance and insurance, and industrial and technical services.",
        body,
        schemas=(jsonld_breadcrumb("industries", "Industries"),),
    )


def listings():
    body = f"""
<section class="phero">
  <div class="wrap">
    <p class="crumbs"><a href="/">Home</a><span>/</span>Listings</p>
    <h1>Florida businesses for sale.</h1>
    <p class="lede">Current opportunities are published on the national listing platforms and the
    Business Brokers of Florida network. Tell Warren what you are looking for and he will send
    what fits &mdash; including businesses that are not publicly listed.</p>
    <div class="btn-row">
      {btn('/contact', 'Set up a buyer search', 'g')}
      {btn('tel:' + SITE['tel_href'], 'Call or text ' + SITE['tel_display'], 'o')}
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="lp rv">
      <div class="lp__hd">
        <div>
          <p class="eyebrow" style="margin-bottom:.8rem">Live listings</p>
          <h2 style="font-size:clamp(1.5rem,2.6vw,2rem)">Warren's current inventory</h2>
        </div>
        <span class="lp__tag">Updated continuously</span>
      </div>
      <p>Listings move quickly, so rather than mirror them here, these profiles are the live
      source &mdash; each one shows every business Warren currently has on the market, with asking
      price, cash flow and location.</p>
      <div class="btn-row">
        {btn(SITE['social']['bizbuysell'], 'View on BizBuySell', 'p', True)}
        {btn(SITE['social']['bizquest'], 'View on BizQuest', 'o', True)}
      </div>
    </div>
  </div>
</section>

<section class="sec" style="padding-top:0">
  <div class="wrap">
    <div style="max-width:62ch;margin-bottom:clamp(2.5rem,5vw,3.5rem)" class="rv">
      <p class="eyebrow">What to look at</p>
      <h2>Browse by what matters to you.</h2>
    </div>
    <div class="grid g3">
      <div class="card rv">
        {icon('badge')}
        <h3>Lender pre-qualified</h3>
        <p>Businesses an SBA lender has already reviewed and indicated it would finance, subject to
        buyer qualification. The fastest path from offer to funded closing.</p>
        {tlink('/contact', 'Ask for pre-qualified listings')}
      </div>
      <div class="card rv">
        {icon('shield')}
        <h3>High-revenue companies</h3>
        <p>Typically $1M or more in revenue, where the buyer pool is more sophisticated and
        structure matters as much as price.</p>
        {tlink('/industries', 'Sectors covered')}
      </div>
      <div class="card rv">
        {icon('buy')}
        <h3>Off-market opportunities</h3>
        <p>Owners who would sell to the right buyer but are not formally listed. These surface
        through broker relationships and direct owner contact, not search results.</p>
        {tlink('/contact', 'Register your criteria')}
      </div>
    </div>
  </div>
</section>

<section class="sec dark" style="padding-top:0">
  <div class="wrap" style="padding-top:var(--sec)">
    <div class="grid split">
      <div class="rv">
        <p class="eyebrow">Buyer registration</p>
        <h2>A saved search beats refreshing a listing site.</h2>
        <p class="lede" style="margin-top:1.4rem">Tell Warren your range, industries, geography
        and timeline once. When something fits, you hear about it &mdash; often before it is
        published.</p>
        <div class="btn-row">{btn('/contact', 'Register your criteria', 'g', True)}</div>
      </div>
      <div class="rv">
        <ul class="checks">
          <li>Matched against new listings as they come to market</li>
          <li>First look at Business Brokers of Florida co-brokerage inventory</li>
          <li>Off-market opportunities sourced from owner and advisor relationships</li>
          <li>Guidance on which businesses are already lender pre-qualified</li>
          <li>Honest screening &mdash; you will be told when something is not a fit</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="sec--tight">
  <div class="wrap">
    <p class="form__note" style="max-width:none">Listing information is supplied by business owners
    and is not independently verified unless expressly stated. All information is provided subject
    to a non-disclosure agreement and should be independently confirmed during due diligence.
    Nothing on this page is an offer to sell securities.</p>
  </div>
</section>

{band(
  "Looking for something specific?",
  "Describe the business you want to own and Warren will tell you honestly what is available, "
  "what it costs and whether it can be financed.",
  ("/contact", "Start a buyer conversation"),
)}
"""
    return page(
        "listings",
        "Florida Businesses For Sale",
        "Florida businesses for sale through WIM Services, LLC — including SBA lender "
        "pre-qualified listings, high-revenue companies and off-market opportunities. Register "
        "your buyer criteria with Warren Merrill.",
        body,
        schemas=(jsonld_breadcrumb("listings", "Listings"),),
    )


def about():
    body = f"""
<section class="phero">
  <div class="wrap">
    <p class="crumbs"><a href="/">Home</a><span>/</span>About</p>
    <h1>{SITE['person']}</h1>
    <p class="lede">Business broker and business owner. Fourteen companies built, operated and
    sold across more than thirty years, and the same owner's mindset applied to every client
    transaction since.</p>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="grid split">
      <div class="rv">
        <div class="folio">
          <div class="folio__ph">
            <p class="folio__phtxt">Portrait<br>{SITE['person']}<br>to be added</p>
          </div>
          <dl>
            <dt>Role</dt>
            <dd>{SITE['role']}<br>{SITE['name']}</dd>
            <dt>Licensed</dt>
            <dd>Florida Real Estate Broker<br>{SITE['broker_lic']}</dd>
            <dt>Brokerage</dt>
            <dd>{SITE['name']}<br>{SITE['brokerage_lic']}</dd>
            <dt>Advisory</dt>
            <dd>WBM B2B Business Consulting<br><span style="color:var(--slate-2);font-size:.86rem">Non&ndash;real estate services</span></dd>
          </dl>
          <div class="folio__div"></div>
          <dl>
            <dt>Direct</dt>
            <dd><a href="tel:{SITE['tel_href']}" style="text-decoration:none;border-bottom:1px solid var(--line)">{SITE['tel_display']}</a></dd>
            <dt>Email</dt>
            <dd><a href="mailto:{SITE['email']}" style="text-decoration:none;border-bottom:1px solid var(--line);word-break:break-word">{SITE['email']}</a></dd>
          </dl>
        </div>
      </div>
      <div class="rv">
        <p class="eyebrow">Background</p>
        <h2>Thirty years on the other side of the table.</h2>
        <p class="lede" style="margin-top:1.4rem">Over his career Warren has built, operated and
        sold fourteen businesses across the Main Street and lower middle-market sectors &mdash;
        having been both the buyer and the seller, he understands the decisions and the pressure
        on each side of a transaction.</p>
        <p>Those ventures spanned construction, convenience stores, manufacturing, professional
        services, real estate, restaurants, retail and service-based companies. Each was created
        and grown hands-on, and each led to a profitable exit. Beyond his own companies, he has
        represented numerous owners and buyers through the complexities of getting a deal closed.</p>
        <p>Today he works with business owners and buyers throughout Florida, focusing on Main
        Street and lower middle-market deals, and guiding clients from initial discussions through
        closing with a clear, organised and practical approach. The emphasis is on preparation,
        communication and execution &mdash; approaching each engagement with an owner's mindset,
        focused on the right outcome and on getting the deal done.</p>
        <blockquote class="pq" style="margin-top:2.2rem">
          I approach each engagement with the same mindset I had as an owner.
          <cite>{SITE['person']}</cite>
        </blockquote>
      </div>
    </div>
  </div>
</section>

<section class="sec dark">
  <div class="wrap">
    <div style="max-width:60ch;margin-bottom:clamp(2.5rem,5vw,3.5rem)" class="rv">
      <p class="eyebrow">Credentials &amp; affiliations</p>
      <h2>Licensed, affiliated and accountable.</h2>
    </div>
    <div class="grid g4">
      <div class="card card--flat rv">
        {icon('badge')}
        <h3 style="font-size:1.15rem">Florida Real Estate Broker</h3>
        <p>Licence {SITE['broker_lic']}. {SITE['name']} holds brokerage licence
        {SITE['brokerage_lic']}.</p>
      </div>
      <div class="card card--flat rv">
        {icon('shield')}
        <h3 style="font-size:1.15rem">Business Brokers of Florida</h3>
        <p>Member office in the largest co-brokering association serving the business brokerage
        profession &mdash; which means statewide reach on both sides of a deal.</p>
      </div>
      <div class="card card--flat rv">
        {icon('badge')}
        <h3 style="font-size:1.15rem">IBBA</h3>
        <p>Member of the International Business Brokers Association since December 2021.</p>
      </div>
      <div class="card card--flat rv">
        {icon('advice')}
        <h3 style="font-size:1.15rem">Community association management</h3>
        <p>Also licensed in Florida as a Community Association Manager ({SITE['cam_lic']}), with
        {SITE['short']} licensed as a CAM firm ({SITE['cab_lic']}).</p>
      </div>
    </div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="grid split">
      <div class="rv">
        <p class="eyebrow">What that means for you</p>
        <h2>Experience you can actually use.</h2>
      </div>
      <div class="rv">
        <ul class="checks">
          <li>A valuation grounded in what buyers and lenders are paying now, not a flattering number</li>
          <li>Recast financials prepared the way an SBA underwriter expects to see them</li>
          <li>Buyer screening that filters out the merely curious before they see your books</li>
          <li>Deal structures that survive diligence, funding and the transition period</li>
          <li>Co-brokerage reach across the Business Brokers of Florida network statewide</li>
          <li>A straight answer when the honest answer is &ldquo;not yet&rdquo;</li>
        </ul>
        <div class="btn-row">
          {btn('/contact', 'Start a conversation', 'p', True)}
          {btn(SITE['social']['linkedin'], 'Connect on LinkedIn', 'o')}
        </div>
      </div>
    </div>
  </div>
</section>

{band(
  "&ldquo;" + SITE["tagline"] + "&rdquo;",
  "Every engagement starts with a confidential conversation &mdash; no cost, no obligation, and "
  "nothing shared outside the room.",
)}
"""
    return page(
        "about",
        "About Warren B. Merrill | Florida Business Broker",
        "Warren B. Merrill has built, operated and sold 14 of his own businesses over 30+ years. "
        "Florida Licensed Real Estate Broker BK-3514191, member of Business Brokers of Florida and "
        "the IBBA, serving Main Street and lower middle-market companies statewide.",
        body,
        schemas=(jsonld_person(), jsonld_breadcrumb("about", "About")),
    )


def contact():
    body = f"""
<section class="phero">
  <div class="wrap">
    <p class="crumbs"><a href="/">Home</a><span>/</span>Contact</p>
    <h1>Start a confidential conversation.</h1>
    <p class="lede">Whether you are twelve months from an exit, actively looking to buy, or simply
    want to know what your business is worth &mdash; the first conversation costs nothing and stays
    between us.</p>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="grid split">
      <div class="rv">
        <p class="eyebrow">Reach Warren directly</p>
        <h2>Call, text or email.</h2>
        <p class="lede" style="margin-top:1.4rem">Warren answers his own phone. For anything
        time-sensitive, a call or text is fastest.</p>
        <dl class="ctiles" style="margin-top:2.2rem">
          <div class="ctile">
            <div class="ctile__ico">{inline_icon('phone')}</div>
            <div>
              <dt>Call or text</dt>
              <dd><a href="tel:{SITE['tel_href']}">{SITE['tel_display']}</a></dd>
            </div>
          </div>
          <div class="ctile">
            <div class="ctile__ico">{inline_icon('mail')}</div>
            <div>
              <dt>Email</dt>
              <dd><a href="mailto:{SITE['email']}">{SITE['email']}</a></dd>
            </div>
          </div>
          <div class="ctile">
            <div class="ctile__ico">{inline_icon('pin')}</div>
            <div>
              <dt>Office</dt>
              <dd>{SITE['offices'][0]['street']}<br>{SITE['offices'][0]['locality']}, {SITE['offices'][0]['region']} {SITE['offices'][0]['zip']}</dd>
            </div>
          </div>
          <div class="ctile">
            <div class="ctile__ico">{inline_icon('clock')}</div>
            <div>
              <dt>Service area</dt>
              <dd>Florida statewide, with the most activity in Central Florida and along the I-4
              corridor and Gulf Coast.</dd>
            </div>
          </div>
          <div class="ctile">
            <div class="ctile__ico">{inline_icon('shield')}</div>
            <div>
              <dt>Confidentiality</dt>
              <dd>Inquiries are treated as confidential. Detailed business information is released
              only under a non-disclosure agreement.</dd>
            </div>
          </div>
        </dl>
      </div>
      <div class="rv">
        <div class="lp">
          <p class="eyebrow" style="margin-bottom:.8rem">Send a message</p>
          <h2 style="font-size:clamp(1.5rem,2.6vw,2rem);margin-bottom:1.6rem">Confidential inquiry</h2>
          {contact_form('contact')}
        </div>
      </div>
    </div>
  </div>
</section>

{band(
  "Prefer to just talk it through?",
  "Call or text and you will reach Warren, not a call centre. Evenings and weekends are fine.",
  ("tel:" + SITE["tel_href"], "Call or text " + SITE["tel_display"]),
  ("mailto:" + SITE["email"], "Send an email"),
)}
"""
    return page(
        "contact",
        "Contact Warren Merrill | WIM Services, LLC",
        "Contact Warren B. Merrill at WIM Services, LLC for a confidential business valuation, "
        "sale or acquisition in Florida. Call or text 360.904.4060 or email "
        "warren@wimservicesllc.com. Offices in Sarasota and Orlando.",
        body,
        schemas=(jsonld_org(), jsonld_breadcrumb("contact", "Contact")),
    )


def privacy():
    body = f"""
<section class="phero">
  <div class="wrap">
    <p class="crumbs"><a href="/">Home</a><span>/</span>Privacy</p>
    <h1>Privacy Policy</h1>
    <p class="lede">How {SITE['name']} collects, uses and protects information submitted through
    this website.</p>
  </div>
</section>
<section class="sec">
  <div class="wrap wrap--narrow" style="font-size:1rem">
    <p style="color:var(--slate-2);font-size:.88rem">Last updated: {date.today().strftime('%B %-d, %Y') if os.name != 'nt' else date.today().strftime('%B %d, %Y')}</p>

    <h2 style="margin-top:2.4rem">Who we are</h2>
    <p>{SITE['name']} ({SITE['brokerage_lic']}), also doing business as {SITE['dba']}, is a
    licensed Florida real estate brokerage providing business brokerage and advisory services.
    Contact: <a href="mailto:{SITE['email']}">{SITE['email']}</a> or {SITE['tel_display']}.</p>

    <h2 style="margin-top:2.4rem">Information we collect</h2>
    <p>We collect only what you choose to send us. Through the contact form that is your name,
    email address, phone number, the nature of your inquiry, and any details you add about your
    business, price range or timeline. If you contact us by phone or email we keep the
    correspondence and any information you provide in it.</p>
    <p>Our web host records standard technical information such as IP address, browser type and
    pages requested, for security and reliability purposes.</p>

    <h2 style="margin-top:2.4rem">How we use it</h2>
    <p>To respond to your inquiry, to provide brokerage and advisory services, to match buyers
    with suitable listings, and to meet our legal, licensing and record-keeping obligations as a
    Florida real estate brokerage.</p>
    <p><strong>We do not sell or share your personal information with third parties for their
    marketing purposes.</strong></p>

    <h2 style="margin-top:2.4rem">Confidentiality</h2>
    <p>Business brokerage depends on confidentiality. Information about a business for sale,
    including its identity and financial details, is released only to prospects who have executed
    a non-disclosure agreement and demonstrated financial capability. If you are an owner
    considering a sale, your inquiry is not disclosed to other parties.</p>

    <h2 style="margin-top:2.4rem">How we share information</h2>
    <p>We share information only as needed to do the work or as required by law:</p>
    <ul class="checks" style="margin:1.2rem 0">
      <li>Cloudflare, Inc. &mdash; website hosting and security</li>
      <li>Our form delivery provider, which transmits form submissions to our email inbox</li>
      <li>Our business email provider</li>
      <li>Co-operating brokers, lenders, attorneys, accountants and closing agents, where
      necessary to progress a transaction you have engaged us on</li>
      <li>Regulators, or others, where required by law or to protect legal rights</li>
    </ul>

    <h2 style="margin-top:2.4rem">Cookies and analytics</h2>
    <p>This site does not use advertising cookies, remarketing pixels or cross-site tracking.
    If website analytics are added in future, this policy will be updated before they go live,
    and opt-out information will be provided.</p>

    <h2 style="margin-top:2.4rem">Text messages</h2>
    <p>If you give us your mobile number we may call or text you about your inquiry. Message and
    data rates may apply. Reply STOP to opt out of further messages, or HELP for help. We do not
    sell or share your SMS opt-in data or personal information with third parties for marketing
    purposes. No mobile information will be shared with third parties or affiliates for marketing
    or promotional purposes.</p>

    <h2 style="margin-top:2.4rem">Retention</h2>
    <p>Inquiries are kept as long as needed to respond and to meet brokerage record-keeping
    requirements under Florida law. You may ask us to delete your information at any time by
    emailing <a href="mailto:{SITE['email']}">{SITE['email']}</a>, subject to records we are
    required to retain.</p>

    <h2 style="margin-top:2.4rem">Your choices</h2>
    <p>You can ask what information we hold about you, ask us to correct it, or ask us to delete
    it. Email <a href="mailto:{SITE['email']}">{SITE['email']}</a>.</p>

    <h2 style="margin-top:2.4rem">Children</h2>
    <p>This site is intended for adults and is not directed at children under 13. We do not
    knowingly collect information from children.</p>

    <h2 style="margin-top:2.4rem">Changes</h2>
    <p>We may update this policy. The revision date at the top of the page shows when it last
    changed.</p>
  </div>
</section>
"""
    return page(
        "privacy",
        "Privacy Policy",
        f"Privacy Policy for {SITE['name']} — what information we collect through this website, "
        "how it is used, and how confidentiality is maintained in business brokerage.",
        body,
        schemas=(jsonld_breadcrumb("privacy", "Privacy Policy"),),
    )


def terms():
    body = f"""
<section class="phero">
  <div class="wrap">
    <p class="crumbs"><a href="/">Home</a><span>/</span>Terms</p>
    <h1>Terms of Service</h1>
    <p class="lede">The terms on which this website is provided.</p>
  </div>
</section>
<section class="sec">
  <div class="wrap wrap--narrow" style="font-size:1rem">
    <p style="color:var(--slate-2);font-size:.88rem">Last updated: {date.today().strftime('%B %-d, %Y') if os.name != 'nt' else date.today().strftime('%B %d, %Y')}</p>

    <h2 style="margin-top:2.4rem">Acceptance</h2>
    <p>By using this website you agree to these terms. If you do not agree, please do not use the
    site.</p>

    <h2 style="margin-top:2.4rem">About us</h2>
    <p>{SITE['name']} ({SITE['brokerage_lic']}), also doing business as {SITE['dba']}, is a
    licensed Florida real estate brokerage. {SITE['person']} is a Florida Licensed Real Estate
    Broker, licence {SITE['broker_lic']}. WBM B2B Business Consulting provides business advisory
    services; business consulting is a non&ndash;real estate service and is not provided under the
    brokerage licence.</p>

    <h2 style="margin-top:2.4rem">No professional advice</h2>
    <p>Information on this site is general in nature and is not legal, tax, accounting, investment
    or securities advice, and must not be relied on as such. Buying or selling a business is a
    significant transaction; you should obtain independent legal, tax and accounting advice before
    acting.</p>

    <h2 style="margin-top:2.4rem">No offer; listing information</h2>
    <p>Nothing on this site is an offer to buy or sell any business, security or interest, or a
    solicitation of such an offer. Listing information, financial figures and business descriptions
    are supplied by business owners and are not independently verified by us unless expressly
    stated. All such information must be independently confirmed by a prospective buyer during due
    diligence.</p>

    <h2 style="margin-top:2.4rem">Confidentiality and non-disclosure</h2>
    <p>Detailed information about a business for sale is provided only after a prospective buyer
    executes a non-disclosure agreement and demonstrates financial capability. Using information
    obtained from us to approach a business owner, their employees, customers or suppliers outside
    the brokerage relationship is prohibited.</p>

    <h2 style="margin-top:2.4rem">Engagements and fees</h2>
    <p>No brokerage or advisory relationship is created by using this site or by submitting an
    inquiry. Any engagement is governed by a separate written agreement signed by both parties,
    which sets out the scope, term and any fee. Sell-side fees are success-based and payable at
    closing unless the written agreement states otherwise. There is no charge for an initial
    consultation.</p>

    <h2 style="margin-top:2.4rem">Acceptable use</h2>
    <p>Do not attempt to interfere with the site, access it by automated means for bulk data
    collection, or use it for any unlawful purpose. Content on this site is our property or used
    with permission and may not be reproduced without written consent.</p>

    <h2 style="margin-top:2.4rem">Third-party links</h2>
    <p>We link to third-party sites, including national business listing platforms. We are not
    responsible for their content, accuracy or privacy practices.</p>

    <h2 style="margin-top:2.4rem">SMS Terms</h2>
    <p>If you provide a mobile number, {SITE['name']} may send you text messages relating to your
    inquiry or transaction. Message frequency varies by conversation. Message and data rates may
    apply. Reply STOP to cancel or HELP for help, or contact
    <a href="mailto:{SITE['email']}">{SITE['email']}</a> or {SITE['tel_display']}. Consent to
    receive messages is not a condition of any purchase or service. Carriers are not liable for
    delayed or undelivered messages.</p>

    <h2 style="margin-top:2.4rem">Disclaimer and limitation of liability</h2>
    <p>This site is provided &ldquo;as is&rdquo; without warranties of any kind, express or
    implied, including as to accuracy, completeness or fitness for a particular purpose. To the
    fullest extent permitted by law, {SITE['name']} is not liable for any indirect, incidental,
    consequential or punitive damages arising from your use of this site or reliance on its
    content.</p>

    <h2 style="margin-top:2.4rem">Governing law</h2>
    <p>These terms are governed by the laws of the State of Florida, without regard to its
    conflict-of-laws rules. Any dispute shall be brought in the state or federal courts located
    in Florida.</p>

    <h2 style="margin-top:2.4rem">Fair housing and equal opportunity</h2>
    <p>As a licensed Florida real estate brokerage, we comply with all applicable federal and
    state fair housing and equal opportunity laws.</p>

    <h2 style="margin-top:2.4rem">Changes</h2>
    <p>We may update these terms. Continued use of the site after changes are posted constitutes
    acceptance of the revised terms.</p>

    <h2 style="margin-top:2.4rem">Contact</h2>
    <p>{SITE['name']}<br>
    {SITE['offices'][0]['street']}, {SITE['offices'][0]['locality']}, {SITE['offices'][0]['region']} {SITE['offices'][0]['zip']}<br>
    <a href="mailto:{SITE['email']}">{SITE['email']}</a> &middot; {SITE['tel_display']}</p>
  </div>
</section>
"""
    return page(
        "terms",
        "Terms of Service",
        f"Terms of Service for the {SITE['name']} website, including listing information "
        "disclaimers, confidentiality requirements and Florida governing law.",
        body,
        schemas=(jsonld_breadcrumb("terms", "Terms of Service"),),
    )


def notfound():
    body = f"""
<section class="phero" style="padding-bottom:clamp(64px,9vw,112px)">
  <div class="wrap">
    <p class="eyebrow">Error 404</p>
    <h1>That page is not here.</h1>
    <p class="lede">The link may be out of date, or the page may have moved. Here is the way
    back.</p>
    <div class="btn-row">
      {btn('/', 'Go to the homepage', 'g')}
      {btn('/contact', 'Contact Warren', 'o')}
    </div>
    <div class="chips" style="margin-top:2.6rem">
      <a class="chip" href="/selling-a-business" style="color:rgba(247,244,239,.8);border-color:var(--line-dk)">Selling a business</a>
      <a class="chip" href="/buying-a-business" style="color:rgba(247,244,239,.8);border-color:var(--line-dk)">Buying a business</a>
      <a class="chip" href="/listings" style="color:rgba(247,244,239,.8);border-color:var(--line-dk)">Businesses for sale</a>
      <a class="chip" href="/industries" style="color:rgba(247,244,239,.8);border-color:var(--line-dk)">Industries</a>
      <a class="chip" href="/about" style="color:rgba(247,244,239,.8);border-color:var(--line-dk)">About Warren</a>
    </div>
  </div>
</section>
"""
    return page("404", "Page not found", "That page could not be found.", body, noindex=True)


# --------------------------------------------------------------------------
# static extras
# --------------------------------------------------------------------------

FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="6" fill="#0C1722"/>
<text x="32" y="44" font-family="Georgia,'Times New Roman',serif" font-size="34"
      text-anchor="middle" fill="#D9AE63">W</text>
</svg>
"""

HEADERS = """/*
  X-Content-Type-Options: nosniff
  X-Frame-Options: SAMEORIGIN
  Referrer-Policy: strict-origin-when-cross-origin
  Permissions-Policy: geolocation=(), microphone=(), camera=()
  Strict-Transport-Security: max-age=31536000; includeSubDomains
  Cross-Origin-Opener-Policy: same-origin-allow-popups

/fonts/*
  Cache-Control: public, max-age=604800, immutable

/assets/*
  Cache-Control: public, max-age=604800

/css/*
  Cache-Control: no-cache

/js/*
  Cache-Control: no-cache
"""

# 301s from the old wbmconsulting.co URL structure, so links keep working.
REDIRECTS = """/selling-a-business.html   /selling-a-business   301
/buying-a-business.html    /buying-a-business    301
/about.html                /about                301
/contact.html              /contact              301
/privacy.html              /privacy              301
/terms.html                /terms                301
/services                  /industries           301
/services.html             /industries           301
/business-listings         /listings             301
/businesses-for-sale       /listings             301
/businesses-for-purchase   /listings             301
/lender-pre-qualified      /listings             301
/high-revenue-businesses   /listings             301
/business-services         /industries           301
/professional-services     /industries           301
/restaurants-and-liquor    /industries           301
/construction-manufacturing-wholesale /industries 301
/by-region                 /listings             301
/home                      /                     301
/index.html                /                     301
"""

WRANGLER = """{
  "$schema": "node_modules/wrangler/config-schema.json",
  "name": "wim-services",
  "compatibility_date": "2026-11-03",
  "assets": {
    "directory": "./public",
    "html_handling": "auto-trailing-slash",
    "not_found_handling": "404-page"
  }
}
"""


def sitemap(slugs):
    today = date.today().isoformat()
    urls = []
    for slug, prio in slugs:
        loc = SITE["base"] + "/" + ("" if slug == "index" else slug)
        urls.append(
            f"  <url><loc>{loc}</loc><lastmod>{today}</lastmod>"
            f"<changefreq>monthly</changefreq><priority>{prio}</priority></url>"
        )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )


ROBOTS = f"""User-agent: *
Allow: /

Sitemap: {SITE['base']}/sitemap.xml
"""


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------


def write(rel, content):
    path = os.path.join(PUB, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(content)
    return len(content.encode("utf-8"))


def main():
    # fingerprints so visitors never get stale CSS/JS
    css_v = fingerprint(os.path.join(PUB, "css", "site.css"))
    js_v = fingerprint(os.path.join(PUB, "js", "site.js"))

    global page
    base_page = page

    def page_v(*a, **kw):
        kw.setdefault("css_v", css_v)
        kw.setdefault("js_v", js_v)
        return base_page(*a, **kw)

    page = page_v

    built = []
    pages = [
        ("index.html", home(), "index", "1.0"),
        ("selling-a-business.html", selling(), "selling-a-business", "0.9"),
        ("buying-a-business.html", buying(), "buying-a-business", "0.9"),
        ("industries.html", industries(), "industries", "0.8"),
        ("listings.html", listings(), "listings", "0.8"),
        ("about.html", about(), "about", "0.8"),
        ("contact.html", contact(), "contact", "0.7"),
        ("privacy.html", privacy(), "privacy", "0.3"),
        ("terms.html", terms(), "terms", "0.3"),
        ("404.html", notfound(), None, None),
    ]

    for fname, html, slug, prio in pages:
        size = write(fname, html)
        built.append((fname, size))
        if slug:
            pass

    slugs = [(s, p) for _, _, s, p in pages if s]
    write("sitemap.xml", sitemap(slugs))
    write("robots.txt", ROBOTS)
    write("_headers", HEADERS)
    write("_redirects", REDIRECTS)
    write("favicon.svg", FAVICON)

    with open(os.path.join(ROOT, "wrangler.jsonc"), "w", encoding="utf-8") as fh:
        fh.write(WRANGLER)

    print(f"css?v={css_v}  js?v={js_v}\n")
    total = 0
    for fname, size in built:
        total += size
        print(f"  {fname:<28} {size/1024:6.1f} KB")
    print(f"\n  {len(built)} pages, {total/1024:.1f} KB of HTML")
    print("  + sitemap.xml, robots.txt, _headers, _redirects, favicon.svg, wrangler.jsonc")


if __name__ == "__main__":
    main()
