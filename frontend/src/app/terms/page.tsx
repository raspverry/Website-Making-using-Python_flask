import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Terms of Service - PageGuard',
  description: 'PageGuard Terms of Service. Read the terms and conditions for using our web accessibility scanning service.',
};

export default function TermsPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="bg-white rounded-2xl border border-gray-200 p-8 sm:p-12">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Terms of Service</h1>
        <p className="text-sm text-gray-500 mb-8">Last updated: February 13, 2026</p>

        <div className="prose prose-gray max-w-none space-y-8">
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">1. Acceptance of Terms</h2>
            <p className="text-gray-600 leading-relaxed">
              By accessing or using PageGuard (&quot;the Service&quot;), operated by PageGuard (&quot;we,&quot;
              &quot;our,&quot; or &quot;us&quot;), you agree to be bound by these Terms of Service (&quot;Terms&quot;).
              If you do not agree to these Terms, you may not use the Service. We reserve the right to
              update these Terms at any time. Continued use of the Service after changes are posted
              constitutes your acceptance of the revised Terms.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">2. Service Description</h2>
            <p className="text-gray-600 leading-relaxed">
              PageGuard is a web accessibility compliance scanning service that crawls websites to
              detect potential violations of the Web Content Accessibility Guidelines (WCAG) 2.2
              Level AA. The Service provides compliance scores, violation reports, AI-generated fix
              suggestions, and exportable compliance reports. The Service also provides scheduled
              monitoring and email alerts for detected changes in compliance status.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">3. Account Responsibilities</h2>
            <p className="text-gray-600 leading-relaxed mb-3">
              To use PageGuard, you must create an account with accurate and complete information.
              You are responsible for:
            </p>
            <ul className="list-disc list-inside text-gray-600 space-y-1 ml-4">
              <li>Maintaining the confidentiality of your account credentials</li>
              <li>All activities that occur under your account</li>
              <li>Notifying us immediately of any unauthorized use of your account</li>
              <li>Ensuring the information you provide is accurate and up-to-date</li>
            </ul>
            <p className="text-gray-600 leading-relaxed mt-3">
              You must be at least 18 years old or the age of majority in your jurisdiction to create
              an account. We reserve the right to suspend or terminate accounts that violate these Terms.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">4. Acceptable Use Policy</h2>
            <p className="text-gray-600 leading-relaxed mb-3">
              You agree to use PageGuard only for lawful purposes and in accordance with these Terms.
              You may only scan websites that you own or have explicit authorization to scan. You agree
              NOT to:
            </p>
            <ul className="list-disc list-inside text-gray-600 space-y-1 ml-4">
              <li>Scan websites you do not own or manage without the owner&apos;s written permission</li>
              <li>Use the Service to perform denial-of-service attacks or overload third-party servers</li>
              <li>Attempt to bypass rate limits, subscription restrictions, or access controls</li>
              <li>Use the Service to gather competitive intelligence on other scanning tools</li>
              <li>Resell, sublicense, or redistribute the Service unless you have an Agency plan with white-label rights</li>
              <li>Reverse engineer, decompile, or disassemble any part of the Service</li>
              <li>Upload malicious content or attempt to compromise the security of the Service</li>
              <li>Use automated scripts to access the Service outside of our published API</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">5. Subscription and Billing</h2>
            <p className="text-gray-600 leading-relaxed mb-3">
              PageGuard offers both free and paid subscription plans. By subscribing to a paid plan,
              you agree to the following:
            </p>
            <ul className="list-disc list-inside text-gray-600 space-y-1 ml-4">
              <li><strong>Billing Cycle:</strong> Subscriptions are billed monthly. Your billing cycle starts on the date you subscribe</li>
              <li><strong>Payment:</strong> All payments are processed securely through Stripe. You authorize us to charge your payment method on file for recurring subscription fees</li>
              <li><strong>Price Changes:</strong> We may adjust pricing with at least 30 days&apos; notice. Existing subscribers will be grandfathered at their current rate for one billing cycle after notification</li>
              <li><strong>Cancellation:</strong> You may cancel your subscription at any time. Cancellation takes effect at the end of the current billing period. No prorated refunds are provided for partial months</li>
              <li><strong>Free Trial:</strong> If offered, free trial terms will be stated at signup. We will notify you before your trial converts to a paid subscription</li>
              <li><strong>Failed Payments:</strong> If a payment fails, we will attempt to charge your payment method again. After multiple failures, your account may be downgraded to the Free plan</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">6. Important Disclaimer Regarding Compliance</h2>
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-amber-900">
              <p className="font-semibold mb-2">PLEASE READ THIS SECTION CAREFULLY</p>
              <p className="leading-relaxed mb-3">
                PageGuard is an automated scanning tool that checks for common WCAG 2.2 Level AA
                violations using programmatic analysis. Our Service is designed to assist you in
                identifying potential accessibility issues, but it has inherent limitations:
              </p>
              <ul className="list-disc list-inside space-y-1 ml-4">
                <li>Automated tools can only detect approximately 30% of all possible accessibility issues</li>
                <li>A high compliance score from PageGuard does NOT mean your website is fully accessible or legally compliant with the ADA, Section 508, or any other law or regulation</li>
                <li>Our scan results should NOT be used as legal evidence of compliance</li>
                <li>Our AI-generated fix suggestions are provided as guidance only and may not resolve all accessibility barriers</li>
              </ul>
              <p className="leading-relaxed mt-3 font-medium">
                We strongly recommend combining PageGuard&apos;s automated scanning with manual
                accessibility audits conducted by qualified accessibility experts. You should also
                consult with legal counsel regarding your specific compliance obligations. PageGuard
                is NOT a substitute for professional accessibility auditing or legal advice.
              </p>
            </div>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">7. Limitation of Liability</h2>
            <p className="text-gray-600 leading-relaxed">
              TO THE MAXIMUM EXTENT PERMITTED BY APPLICABLE LAW, PAGEGUARD AND ITS OFFICERS,
              DIRECTORS, EMPLOYEES, AND AGENTS SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL,
              SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, INCLUDING BUT NOT LIMITED TO: LOSS OF
              PROFITS, DATA, USE, OR GOODWILL; COSTS OF PROCUREMENT OF SUBSTITUTE SERVICES; OR ANY
              DAMAGES ARISING FROM (A) YOUR USE OF OR INABILITY TO USE THE SERVICE, (B) ANY THIRD-PARTY
              CLAIMS OF ACCESSIBILITY NON-COMPLIANCE AGAINST YOU, (C) RELIANCE ON SCAN RESULTS OR
              AI-GENERATED FIX SUGGESTIONS, OR (D) UNAUTHORIZED ACCESS TO OR ALTERATION OF YOUR DATA.
              OUR TOTAL LIABILITY FOR ALL CLAIMS ARISING FROM THESE TERMS OR THE SERVICE SHALL NOT
              EXCEED THE AMOUNT YOU PAID US IN THE 12 MONTHS PRECEDING THE CLAIM.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">8. Warranty Disclaimer</h2>
            <p className="text-gray-600 leading-relaxed">
              THE SERVICE IS PROVIDED &quot;AS IS&quot; AND &quot;AS AVAILABLE&quot; WITHOUT WARRANTIES OF
              ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO IMPLIED WARRANTIES OF
              MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT. WE DO NOT WARRANT
              THAT THE SERVICE WILL BE UNINTERRUPTED, ERROR-FREE, OR COMPLETELY SECURE, OR THAT OUR
              SCANS WILL DETECT ALL ACCESSIBILITY VIOLATIONS ON YOUR WEBSITE.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">9. Intellectual Property</h2>
            <p className="text-gray-600 leading-relaxed">
              The Service, including its design, features, content, and underlying technology, is the
              property of PageGuard and is protected by copyright, trademark, and other intellectual
              property laws. You retain ownership of the websites you scan and the content therein.
              We retain ownership of all scan reports, compliance scores, AI-generated suggestions,
              and other outputs generated by the Service. You are granted a non-exclusive license to
              use these outputs for your own internal business purposes. The PageGuard compliance badge,
              when earned, may be displayed on your website subject to our badge usage guidelines.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">10. Termination</h2>
            <p className="text-gray-600 leading-relaxed">
              We may terminate or suspend your account and access to the Service immediately, without
              prior notice or liability, if you breach these Terms, engage in abusive scanning behavior,
              or for any other reason at our sole discretion. Upon termination, your right to use the
              Service will cease immediately. You may request an export of your data within 30 days
              of termination. After 30 days, your data will be permanently deleted in accordance with
              our Privacy Policy.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">11. Indemnification</h2>
            <p className="text-gray-600 leading-relaxed">
              You agree to indemnify, defend, and hold harmless PageGuard and its officers, directors,
              employees, and agents from and against any claims, liabilities, damages, losses, and
              expenses (including reasonable attorney&apos;s fees) arising out of or in connection with:
              (a) your use of the Service, (b) your violation of these Terms, (c) your violation of any
              third-party rights, or (d) any claim that your use of the Service caused damage to a
              third party.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">12. Changes to Terms</h2>
            <p className="text-gray-600 leading-relaxed">
              We reserve the right to modify these Terms at any time. Material changes will be
              communicated via email to the address associated with your account and by posting an
              updated version on this page. Changes take effect 30 days after notification for existing
              users. Your continued use of the Service after the effective date constitutes acceptance
              of the revised Terms. If you do not agree with the changes, you must stop using the
              Service and cancel your subscription.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">13. Governing Law and Disputes</h2>
            <p className="text-gray-600 leading-relaxed">
              These Terms shall be governed by and construed in accordance with the laws of the State
              of Delaware, United States, without regard to its conflict of law provisions. Any disputes
              arising from these Terms or the Service shall first be resolved through good-faith
              negotiation. If negotiation fails, disputes shall be resolved through binding arbitration
              in accordance with the rules of the American Arbitration Association. You agree to waive
              any right to participate in class action lawsuits or class-wide arbitration.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">14. Severability</h2>
            <p className="text-gray-600 leading-relaxed">
              If any provision of these Terms is found to be unenforceable or invalid, that provision
              shall be limited or eliminated to the minimum extent necessary so that these Terms shall
              otherwise remain in full force and effect.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">15. Contact Us</h2>
            <p className="text-gray-600 leading-relaxed">
              If you have questions about these Terms of Service, please contact us at:
            </p>
            <div className="mt-3 bg-gray-50 rounded-lg p-4 text-gray-600">
              <p><strong>PageGuard</strong></p>
              <p>Email: <a href="mailto:legal@pageguard.dev" className="text-blue-600 hover:text-blue-700 underline">legal@pageguard.dev</a></p>
              <p>Website: <a href="https://pageguard.dev" className="text-blue-600 hover:text-blue-700 underline">pageguard.dev</a></p>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
