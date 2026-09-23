# Open Emergency Metadata Protocol (Gray Sky Specification)

**Version:** 1.0.0 (Pilot Release)  
**Author:** [Erik Felton]  
**License:** [MIT License](LICENSE)  

---

## ⚖️ Intellectual Property & Prior Art Declaration
This document defines a novel technical protocol that leverages standard internet architectures (HTML `<meta>` properties and structured JSON-LD blocks) to embed government-standard operational frameworks—specifically **Emergency Support Functions (ESF)** and jurisdictional tiers—directly into the metadata layers of public websites. 

This specification is published openly under the **MIT License** to establish **irrevocable public prior art**. No entity, corporation, or commercial vendor may patent, restrict, or monetize the core `graysky:` metadata namespace properties defined herein. The namespace and syntax rules are preserved forever as free, open-source infrastructure for the global emergency management and volunteer community.

---

## 🧭 Core Concept: The Data Bridge
Commercial web search engines and social media networks optimize web data for consumer sharing using standard Open Graph properties (`og:title`, `og:description`). Consumer tech lacks native awareness of logistical command structures used during active disasters.

The **Gray Sky Protocol (`graysky`)** establishes the missing technical namespace, allowing web crawlers used by Emergency Operations Centers (EOCs) to instantly ingest deterministic, zero-intervention status metrics from field partners without manual paperwork.

---

## 🛠 Technical Specification: Custom Open Graph Extensions

Web administrators can embed these properties directly inside the `<head>` section of their HTML code.

```html
<!-- Standard Consumer Social Media Tags -->
<meta property="og:title" content="Brevard Emergency Amateur Radio Services (BEARS)" />
<meta property="og:description" content="Active regional communication network supporting local emergency operations shelters." />

<!-- Custom Gray Sky Emergency Extensions -->
<meta property="graysky:esf" content="ESF-2" />
<meta property="graysky:tier" content="Local" />
<meta property="graysky:counties" content="Brevard, Orange" />
<meta property="graysky:status" content="Active" />
<meta property="graysky:capacity" content="4_repeaters_online, 12_operators_standby" />
```

### 📋 Property Dictionary Reference

| Meta Property | Accepted Values | Operational EOC Dashboard Impact |
| :--- | :--- | :--- |
| `graysky:esf` | `ESF-1` through `ESF-20` | Dynamically maps the asset to its strict Emergency Support Function role panel. |
| `graysky:tier` | `Local`, `State`, `National` | Controls the 3-tier visual hierarchy color badge on the incident command map. |
| `graysky:counties` | Comma-separated text list | Enforces geographic lockdown parameters, grouping local assets into county filters. |
| `graysky:status` | `Active`, `Standby`, `Standdown`, `Offline` | Triggers the real-time operational status visual alert light (🟢/🟡/🔴). |
| `graysky:capacity` | Custom alphanumeric text | Ingests live logistical metrics directly into senior command panel dossiers. |

---

## 📦 Senior-Accessible Implementation: Structured JSON-LD Data
For modern Content Management Systems (CMS) or site builders where editing header meta tags is restricted, the protocol can alternately be parsed via an isolated script text block inserted anywhere in the site footer code.

```html
<script type="application/ld+json">
{
  "@context": "https://graysky.org",
  "@type": "EmergencyResponseUnit",
  "name": "Brevard Emergency Amateur Radio Services (BEARS)",
  "assignedESF": "ESF-2",
  "jurisdictionTier": "Local",
  "targetCounties": ["Brevard", "Orange"],
  "operationalStatus": "Active",
  "resourceCapacity": "4 repeaters online, 12 operators standby"
}
</script>
```

---

## 💡 Zero-Overhead Adoption Model
This protocol is engineered to operate with **zero financial or technical overhead** for volunteer disaster relief groups (VOADs, CERTs, food banks). Implementation requires less than 5 minutes from a website developer or volunteer web administrator, creating a frictionless, network-wide mechanism for automated resource discovery during active deployments.
