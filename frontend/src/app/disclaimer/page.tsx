import type { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Disclaimer - PageGuard',
  description: 'Important disclaimers about PageGuard accessibility scanning limitations and legal compliance.',
};

export default function DisclaimerPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="bg-white rounded-2xl border border-gray-200 p-8 sm:p-12">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Disclaimer</h1>
        <p className="text-sm text-gray-500 mb-8">Last updated: February 13, 2026</p>

        <div className="bg-amber-50 border border-amber-200 rounded-lg p-6 mb-8">
          <p className="text-amber-900 font-semibold text-lg mb-2">Important: Please Read Carefully</p>
          <p className="text-amber-800 leading-relaxed">
            PageGuard is an automated accessibility scanning tool. While we strive to provide
            accurate and helpful results, there are important limitations you must understand before
            relying on our Service for compliance decisions.
          </p>
        </div>

        <div className="prose prose-gray max-w-none space-y-8">
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">1. What Our Scanner Does</h2>
            <p className="text-gray-600 leading-relaxed">
              PageGuard scans websites for common violations of the Web Content Accessibility
              Guidelines (WCAG) 2.2 Level AA using automated testing methods. Our scanner programmatically
              analyzes your HTML, CSS, and page structure to detect issues such as missing alternative text
              on images, insufficient color contrast, missing form labels, improper heading structure,
              keyboard accessibility problems, and other machine-detectable violations. We currently check
              for 10 high-impact WCAG rules that cover the most common accessibility failures found across
              the web.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">2. Limitations of Automated Testing</h2>
            <p className="text-gray-600 leading-relaxed mb-3">
              It is widely recognized in the accessibility community that automated testing tools have
              significant limitations. According to research by the{' '}
              <a href="https://webaim.org/" className="text-blue-600 hover:text-blue-700 underline" target="_blank" rel="noopener noreferrer">
                WebAIM (Web Accessibility In Mind)
              </a>{' '}
              organization and other accessibility experts:
            </p>
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-900 mb-4">
              <p className="font-semibold">
                Automated tools can only detect approximately 30% of all possible WCAG accessibility
                violations.
              </p>
            </div>
            <p className="text-gray-600 leading-relaxed mb-3">
              The remaining ~70% of accessibility issues require human judgment to identify. Examples
              of issues that automated tools typically cannot detect include:
            </p>
            <ul className="list-disc list-inside text-gray-600 space-y-1 ml-4">
              <li>Whether alternative text on images is meaningful and descriptive (not just present)</li>
              <li>Whether the reading order of content makes logical sense for screen reader users</li>
              <li>Whether video captions are accurate and synchronized</li>
              <li>Whether interactive components are intuitive to navigate with assistive technology</li>
              <li>Whether the overall user experience is accessible and usable for people with disabilities</li>
              <li>Whether ARIA attributes are used correctly in context</li>
              <li>Whether cognitive accessibility requirements are met</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">3. A Passing Score Does Not Mean Full Compliance</h2>
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-amber-900 mb-4">
              <p className="font-semibold leading-relaxed">
                A high compliance score from PageGuard (even 100/100) does NOT mean your website is
                fully accessible or legally compliant with the Americans with Disabilities Act (ADA),
                Section 508, the European Accessibility Act, or any other accessibility law or regulation.
              </p>
            </div>
            <p className="text-gray-600 leading-relaxed">
              Our score reflects only the subset of issues our automated scanner can detect. A site
              scoring 100 on PageGuard could still have significant accessibility barriers that require
              manual testing to discover. You should never assume compliance based solely on automated
              test results from any tool, including PageGuard.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">4. Scan Results Are Not Legal Evidence</h2>
            <p className="text-gray-600 leading-relaxed">
              PageGuard scan results, compliance reports, and compliance scores should NOT be used as
              legal evidence of accessibility compliance in any court, regulatory proceeding, or legal
              dispute. Our reports are informational tools designed to help you identify and fix common
              accessibility issues. They do not constitute a legal certification of compliance with
              the ADA, WCAG, Section 508, or any other standard or regulation.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">5. Our Recommendation: Combine Automated and Manual Testing</h2>
            <p className="text-gray-600 leading-relaxed mb-3">
              For meaningful accessibility compliance, we strongly recommend a multi-layered approach:
            </p>
            <ol className="list-decimal list-inside text-gray-600 space-y-2 ml-4">
              <li>
                <strong>Automated scanning</strong> (like PageGuard) to catch the ~30% of issues that
                can be detected programmatically and to monitor for regressions over time
              </li>
              <li>
                <strong>Manual expert audit</strong> by a qualified accessibility consultant who can
                evaluate the full user experience with assistive technologies
              </li>
              <li>
                <strong>User testing</strong> with people who have disabilities to identify real-world
                usability barriers
              </li>
              <li>
                <strong>Ongoing training</strong> for your development and content teams on
                accessibility best practices
              </li>
              <li>
                <strong>Legal consultation</strong> with an attorney familiar with digital accessibility
                law for your specific jurisdiction and circumstances
              </li>
            </ol>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">6. We Are Not a Law Firm</h2>
            <p className="text-gray-600 leading-relaxed">
              PageGuard is a technology company, not a law firm. We do not provide legal advice, legal
              representation, or legal opinions. Nothing in our Service, reports, documentation, blog
              posts, or communications should be construed as legal advice. The information we provide
              about accessibility laws (including ADA Title II deadlines and WCAG standards) is for
              informational and educational purposes only. For legal advice regarding your specific
              compliance obligations, you should consult a qualified attorney.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">7. ADA Deadline Information</h2>
            <p className="text-gray-600 leading-relaxed">
              PageGuard references the ADA Title II web accessibility compliance deadline of April 24,
              2026 in our marketing and product materials. This information is provided for general
              informational purposes based on publicly available information from the U.S. Department
              of Justice. We make every effort to ensure this information is accurate, but we do not
              guarantee its accuracy, completeness, or applicability to your specific situation. ADA
              compliance requirements may vary based on your organization type, size, and jurisdiction.
              You should verify all regulatory deadlines and requirements with official government
              sources and legal counsel.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">8. AI-Generated Fix Suggestions</h2>
            <p className="text-gray-600 leading-relaxed">
              PageGuard uses artificial intelligence to generate code fix suggestions for detected
              violations. These suggestions are provided as a starting point to assist your development
              team. They should be reviewed by a qualified developer before implementation, as
              AI-generated code may not account for all aspects of your specific codebase, framework,
              or design system. We do not guarantee that implementing AI-generated fixes will resolve
              all accessibility issues or achieve compliance with any standard.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">9. Third-Party Websites</h2>
            <p className="text-gray-600 leading-relaxed">
              PageGuard scans third-party websites at your direction. We are not responsible for the
              content, accessibility, or practices of any website you scan. Our scan results reflect
              the state of the website at the time of scanning and may not reflect subsequent changes.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">10. Questions</h2>
            <p className="text-gray-600 leading-relaxed">
              If you have questions about this Disclaimer, our scanning methodology, or the limitations
              of our Service, please contact us at{' '}
              <a href="mailto:support@pageguard.dev" className="text-blue-600 hover:text-blue-700 underline">
                support@pageguard.dev
              </a>.
            </p>
            <p className="text-gray-600 leading-relaxed mt-4">
              For our full legal terms, please also review our{' '}
              <Link href="/terms" className="text-blue-600 hover:text-blue-700 underline">Terms of Service</Link>
              {' '}and{' '}
              <Link href="/privacy" className="text-blue-600 hover:text-blue-700 underline">Privacy Policy</Link>.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}
