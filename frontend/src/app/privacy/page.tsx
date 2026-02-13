import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Privacy Policy - PageGuard',
  description: 'PageGuard Privacy Policy. Learn how we collect, use, and protect your data.',
};

export default function PrivacyPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="bg-white rounded-2xl border border-gray-200 p-8 sm:p-12">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Privacy Policy</h1>
        <p className="text-sm text-gray-500 mb-8">Last updated: February 13, 2026</p>

        <div className="prose prose-gray max-w-none space-y-8">
          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">1. Introduction</h2>
            <p className="text-gray-600 leading-relaxed">
              PageGuard (&quot;we,&quot; &quot;our,&quot; or &quot;us&quot;) operates the PageGuard web accessibility
              compliance scanning service (the &quot;Service&quot;). This Privacy Policy explains how we collect,
              use, disclose, and safeguard your information when you use our Service. Please read this
              policy carefully. By using PageGuard, you consent to the data practices described in this
              policy.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">2. Information We Collect</h2>
            <h3 className="text-lg font-medium text-gray-800 mb-2">2.1 Account Information</h3>
            <p className="text-gray-600 leading-relaxed mb-3">
              When you create an account, we collect:
            </p>
            <ul className="list-disc list-inside text-gray-600 space-y-1 ml-4">
              <li>Your name</li>
              <li>Email address</li>
              <li>Password (stored in hashed form; we never store plaintext passwords)</li>
            </ul>

            <h3 className="text-lg font-medium text-gray-800 mb-2 mt-4">2.2 Website and Scan Data</h3>
            <p className="text-gray-600 leading-relaxed mb-3">
              When you use our scanning service, we collect:
            </p>
            <ul className="list-disc list-inside text-gray-600 space-y-1 ml-4">
              <li>Website URLs you submit for scanning</li>
              <li>Scan results, including WCAG compliance scores, detected violations, affected HTML elements, and AI-generated fix suggestions</li>
              <li>Scan history and timestamps</li>
            </ul>

            <h3 className="text-lg font-medium text-gray-800 mb-2 mt-4">2.3 Payment Information</h3>
            <p className="text-gray-600 leading-relaxed">
              Payment processing is handled entirely by Stripe, Inc. We do not store your credit card
              number, CVC, or billing address on our servers. We retain only your Stripe customer ID and
              subscription plan details to manage your account.
            </p>

            <h3 className="text-lg font-medium text-gray-800 mb-2 mt-4">2.4 Usage Data</h3>
            <p className="text-gray-600 leading-relaxed">
              We automatically collect certain information when you access our Service, including your
              IP address, browser type, operating system, pages visited, and the date and time of your
              visits. This data is used solely for analytics and improving the Service.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">3. How We Use Your Information</h2>
            <p className="text-gray-600 leading-relaxed mb-3">
              We use the information we collect to:
            </p>
            <ul className="list-disc list-inside text-gray-600 space-y-1 ml-4">
              <li>Provide, maintain, and improve the PageGuard scanning service</li>
              <li>Process your scans and generate accessibility compliance reports</li>
              <li>Generate AI-powered fix suggestions for detected violations</li>
              <li>Send you scan results, alerts about new violations, and service updates</li>
              <li>Process payments and manage your subscription</li>
              <li>Respond to your customer support requests</li>
              <li>Monitor and analyze usage patterns to improve our service</li>
              <li>Enforce our Terms of Service and protect against abuse</li>
            </ul>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">4. Data Retention</h2>
            <p className="text-gray-600 leading-relaxed">
              We retain your account information for as long as your account is active. Scan results
              and compliance reports are retained for 12 months from the date of each scan to allow
              you to track compliance trends over time. When you delete your account, we will delete
              your personal data and scan history within 30 days, except where we are required to
              retain it for legal or regulatory purposes. Aggregated, anonymized data that cannot
              identify you may be retained indefinitely for statistical purposes.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">5. Third-Party Services</h2>
            <p className="text-gray-600 leading-relaxed mb-3">
              We share your data with the following third-party services to operate PageGuard:
            </p>
            <ul className="list-disc list-inside text-gray-600 space-y-2 ml-4">
              <li>
                <strong>Stripe, Inc.</strong> &mdash; Payment processing. Stripe receives your payment
                information directly and is governed by <a href="https://stripe.com/privacy" className="text-blue-600 hover:text-blue-700 underline" target="_blank" rel="noopener noreferrer">Stripe&apos;s Privacy Policy</a>.
              </li>
              <li>
                <strong>OpenAI</strong> &mdash; AI-powered fix suggestions and accessibility analysis.
                When you use AI features, relevant scan data (violation descriptions, HTML elements) is
                sent to OpenAI&apos;s API to generate fix suggestions. OpenAI&apos;s data handling is governed
                by <a href="https://openai.com/policies/privacy-policy" className="text-blue-600 hover:text-blue-700 underline" target="_blank" rel="noopener noreferrer">OpenAI&apos;s Privacy Policy</a>.
                We do not send your personal information (name, email) to OpenAI.
              </li>
            </ul>
            <p className="text-gray-600 leading-relaxed mt-3">
              We do not sell, rent, or trade your personal information to any third party for marketing
              purposes.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">6. Cookies</h2>
            <p className="text-gray-600 leading-relaxed">
              PageGuard uses only essential cookies required for the operation of our Service. These
              include session cookies to maintain your authentication state and security tokens to
              prevent cross-site request forgery. We do not use advertising cookies, tracking cookies,
              or third-party analytics cookies. You can configure your browser to refuse cookies, but
              this may prevent you from using certain features of our Service.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">7. Data Security</h2>
            <p className="text-gray-600 leading-relaxed">
              We implement industry-standard security measures to protect your data, including:
              encryption of data in transit using TLS/SSL, hashed password storage using bcrypt,
              regular security audits, access controls limiting data access to authorized personnel
              only, and secure cloud hosting infrastructure. However, no method of transmission over
              the Internet or electronic storage is 100% secure. While we strive to protect your
              personal information, we cannot guarantee its absolute security.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">8. Your Rights</h2>
            <p className="text-gray-600 leading-relaxed mb-3">
              Depending on your location, you may have the following rights regarding your personal data:
            </p>
            <ul className="list-disc list-inside text-gray-600 space-y-1 ml-4">
              <li><strong>Access:</strong> Request a copy of the personal data we hold about you</li>
              <li><strong>Correction:</strong> Request that we correct inaccurate or incomplete data</li>
              <li><strong>Deletion:</strong> Request that we delete your personal data</li>
              <li><strong>Data Portability:</strong> Request a machine-readable export of your data, including scan results and reports</li>
              <li><strong>Opt-out:</strong> Opt out of marketing communications at any time</li>
              <li><strong>Restriction:</strong> Request that we restrict the processing of your personal data</li>
            </ul>
            <p className="text-gray-600 leading-relaxed mt-3">
              To exercise any of these rights, please contact us at <a href="mailto:privacy@pageguard.dev" className="text-blue-600 hover:text-blue-700 underline">privacy@pageguard.dev</a>.
              We will respond to your request within 30 days.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">9. California Privacy Rights (CCPA)</h2>
            <p className="text-gray-600 leading-relaxed mb-3">
              If you are a California resident, the California Consumer Privacy Act (CCPA) grants you
              additional rights:
            </p>
            <ul className="list-disc list-inside text-gray-600 space-y-1 ml-4">
              <li><strong>Right to Know:</strong> You may request disclosure of the categories and specific pieces of personal information we have collected about you in the past 12 months</li>
              <li><strong>Right to Delete:</strong> You may request deletion of your personal information, subject to certain exceptions</li>
              <li><strong>Right to Opt-Out:</strong> We do not sell personal information. If this changes, you will have the right to opt out</li>
              <li><strong>Right to Non-Discrimination:</strong> We will not discriminate against you for exercising your CCPA rights</li>
            </ul>
            <p className="text-gray-600 leading-relaxed mt-3">
              To exercise your CCPA rights, contact us at <a href="mailto:privacy@pageguard.dev" className="text-blue-600 hover:text-blue-700 underline">privacy@pageguard.dev</a>.
              We may need to verify your identity before processing your request.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">10. GDPR (European Users)</h2>
            <p className="text-gray-600 leading-relaxed">
              If you are located in the European Economic Area (EEA), you have rights under the General
              Data Protection Regulation (GDPR), including the rights listed in Section 8 above. Our
              legal basis for processing your personal data includes: your consent, the performance of
              our contract with you (providing the Service), and our legitimate interests in operating
              and improving the Service. You may lodge a complaint with your local data protection
              authority if you believe we have violated your data protection rights.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">11. Children&apos;s Privacy</h2>
            <p className="text-gray-600 leading-relaxed">
              PageGuard is not directed at children under the age of 13. We do not knowingly collect
              personal information from children under 13. If we discover that a child under 13 has
              provided us with personal information, we will promptly delete it. If you are a parent or
              guardian and believe your child has provided us with personal information, please contact
              us at <a href="mailto:privacy@pageguard.dev" className="text-blue-600 hover:text-blue-700 underline">privacy@pageguard.dev</a>.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">12. Changes to This Policy</h2>
            <p className="text-gray-600 leading-relaxed">
              We may update this Privacy Policy from time to time. We will notify you of any material
              changes by posting the new policy on this page and updating the &quot;Last updated&quot; date.
              For significant changes, we will send you an email notification. Your continued use of the
              Service after any changes constitutes your acceptance of the updated policy.
            </p>
          </section>

          <section>
            <h2 className="text-xl font-semibold text-gray-900 mb-3">13. Contact Us</h2>
            <p className="text-gray-600 leading-relaxed">
              If you have questions or concerns about this Privacy Policy or our data practices, please
              contact us at:
            </p>
            <div className="mt-3 bg-gray-50 rounded-lg p-4 text-gray-600">
              <p><strong>PageGuard</strong></p>
              <p>Email: <a href="mailto:privacy@pageguard.dev" className="text-blue-600 hover:text-blue-700 underline">privacy@pageguard.dev</a></p>
              <p>Website: <a href="https://pageguard.dev" className="text-blue-600 hover:text-blue-700 underline">pageguard.dev</a></p>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
