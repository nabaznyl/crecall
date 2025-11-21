# CRECALL BRAND LICENSE & PROTECTIVE AGREEMENT (PRELIMINARY DRAFT)

THIS DOCUMENT ("Agreement") ESTABLISHES THE TERMS UNDER WHICH THE OWNER GRANTS LIMITED RIGHTS FOR USE, CREATIONS, AND DISTRIBUTIONS OF SOFTWARE, DOCUMENTATION, AND RELATED MATERIALS UNDER THE "CRECALL" BRAND. THIS IS NOT A SUBSTITUTE FOR FORMAL LEGAL COUNSEL; SEEK PROFESSIONAL REVIEW FOR ENFORCEABILITY.

## 1. DEFINITIONS
- **Owner**: The individual or entity retaining all original and derivative rights to the crecall brand and codebase.
- **Software**: All source code, binaries, scripts, schemas, configurations, and build artifacts under the crecall repository and associated releases.
- **Brand Assets**: Name "crecall", logos, marks, domain references, unique UI identifiers.
- **Derivative Work**: Any modification, enhancement, port, integration, or adaptation based on Software.
- **Distribution**: Any act of providing the Software or Derivative Work copies to third parties via any medium.
- **Creations**: New modules, plugins, integrations, or extensions developed atop the Software.

## 2. OWNERSHIP & RETENTION
All title, interest, and intellectual property rights remain solely with Owner. No transfer of ownership is implied by access, fork, or contribution. Unauthorized claims, trademark dilution, or confusion attempts are prohibited.

## 3. PERMITTED USES
Subject to compliance:
1. Non-commercial experimentation.
2. Internal organizational deployment.
3. Creation of plugins or tools that interoperate without copying protected Brand Assets.
4. Educational demonstration with proper attribution: "Used under license from crecall Owner.".

## 4. RESTRICTED / PROHIBITED USES
You MAY NOT:
- Claim origin or authorship of core Software.
- Remove or obfuscate attribution notices.
- Use Brand Assets to mislead about endorsement or partnership.
- Sell direct copies or minimal modifications as proprietary products.
- Embed undisclosed telemetry, malware, credential harvesting, or backdoors.
- Sub-license rights you do not possess.

## 5. DERIVATIVE WORKS
Derivatives must:
- Provide clear changelog of modifications.
- Preserve this Agreement file.
- Indicate divergence: "This is a derivative of crecall, not official.".
Owner reserves right to request rebranding if confusion risk is present.

## 6. CONTRIBUTIONS
Submitted code, documentation, or ideas become part of Software under this Agreement. Contributor affirms right and originality. Owner may decline, modify, or remove contributions at discretion.

## 7. SECURITY & INTEGRITY COUNTER-MEASURES
To protect against loopholes and shifty practices:
- Mandatory integrity hashing for release artifacts (SHA-256) with published checksums.
- Signed release tags (GPG) for authenticity.
- Automated secret scanning of contributions prior to merge.
- Dependency audit (SCA) pipeline; high severity vulnerabilities must be patched before release.
- Anti-tamper: Any modified official binary must show diffable reproducible build.
- License watermark: Key files include reference to "Owner | creations | distributions" phrase.
- Enforcement triggers: Detect unauthorized forks mimicking official distribution; issue takedown notices.

## 8. PRIVACY & TELEMETRY
If optional telemetry is introduced:
- Must be opt-in, clearly documented, and anonymized.
- No credential, secret, or proprietary source content collection.
- Users may disable fully without functional degradation.

## 9. WARRANTY & LIABILITY
SOFTWARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND. NO LIABILITY FOR DATA LOSS, SECURITY INCIDENTS, OR BUSINESS IMPACT. USERS ASSUME ALL RISK FOR DEPLOYMENT AND OPERATION.

## 10. INDEMNIFICATION
User agrees to indemnify and hold Owner harmless against claims arising from misuse, derivative distribution violations, or security negligence unrelated to official releases.

## 11. TERMINATION
Rights terminate automatically upon violation. Upon termination user must cease use of Brand Assets and remove confusing representations. Continued infringement may trigger formal enforcement.

## 12. DISPUTE RESOLUTION
Parties should seek amicable resolution first. Owner reserves jurisdiction selection in formal disputes unless superseded by mandatory local law.

## 13. AMENDMENTS
Owner may publish revised Agreement versions. Continued use constitutes acceptance. Material changes highlighted in changelog.

## 14. ENFORCEMENT & ANTI-LOOPHOLE CLAUSES
- No implied license through silence, omission, or failure to enforce a breach.
- No derivative may create further restrictions on original upstream beyond this Agreement.
- Attempts to exploit vagueness default toward Owner's protective interpretation.
- Partial invalidity does not void remaining provisions.

## 15. BRAND PROTECTION CLAUSES
- Use of "crecall" in domain names, package registries, or marketplaces requires explicit written permission.
- Confusingly similar names may be challenged (e.g., "krecal", "crecall-pro").
- Owner may issue public authenticity keys; counterfeit distributions lacking signature considered infringing.

## 16. COMPLIANCE CHECKLIST (SUMMARY)
| Requirement | Applies | Status |
|-------------|--------|--------|
| Attribution preserved | All distributions | Must keep |
| Agreement file included | Derivatives | Must include |
| Clear divergence notice | Derivatives | Required |
| No secret collection | Telemetry | Mandatory |
| Signed releases | Official builds | Recommended |
| Integrity hashes | Artifacts | Required |

## 17. KEY PROOF PHRASE
The following phrase MUST appear in protected files and official distributions to validate licensing continuity: "Owner retains rights over creations and distributions under the crecall brand." (Do not remove.)

## 18. ACCEPTANCE
Use, installation, or distribution indicates acceptance of this Agreement.

---
**NOTE:** This is a generic protective draft. Consult qualified legal counsel to finalize enforceable licensing terms for jurisdiction-specific needs.
