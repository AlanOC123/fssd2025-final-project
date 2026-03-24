import { ArrowLeft } from 'lucide-react'

const SECTIONS = [
    {
        title: '1. Acceptance of Terms',
        content: `By accessing or using Apex ("the Platform"), you agree to be bound by these Terms and Conditions. If you do not agree to these terms, please do not use the Platform. These terms apply to all users, including trainers and clients.`,
    },
    {
        title: '2. Description of Service',
        content: `Apex is a personal training platform that facilitates connections between fitness trainers and clients. The Platform provides tools for program creation, workout tracking, session logging, and performance analytics. Apex does not directly provide fitness or health services.`,
    },
    {
        title: '3. User Accounts',
        content: `You are responsible for maintaining the confidentiality of your account credentials and for all activity that occurs under your account. You must provide accurate and complete information when registering. You must be at least 18 years of age to use the Platform. You agree to notify us immediately of any unauthorised use of your account.`,
    },
    {
        title: '4. Trainer and Client Responsibilities',
        content: `Trainers are solely responsible for the accuracy and appropriateness of the programs, workouts, and advice they provide through the Platform. Clients acknowledge that exercise carries inherent risks and agree to consult a qualified medical professional before beginning any training programme. Apex accepts no liability for injury, illness, or adverse outcomes arising from the use of programs or workouts created on the Platform.`,
    },
    {
        title: '5. Acceptable Use',
        content: `You agree not to use the Platform for any unlawful purpose, to harass or harm other users, to upload or transmit harmful, offensive, or infringing content, to attempt to gain unauthorised access to any part of the Platform or its infrastructure, or to interfere with the proper functioning of the Platform.`,
    },
    {
        title: '6. Intellectual Property',
        content: `All content, design, and code comprising the Platform is the property of Apex and is protected by applicable intellectual property laws. Users retain ownership of content they create on the Platform (such as programs and workout plans) but grant Apex a non-exclusive licence to store and display that content for the purpose of providing the service.`,
    },
    {
        title: '7. Privacy and Data',
        content: `Your use of the Platform is subject to our Privacy Policy. By using the Platform, you consent to the collection and use of your data as described therein. We take reasonable measures to protect your personal data but cannot guarantee absolute security of data transmitted over the internet.`,
    },
    {
        title: '8. Uploaded Media',
        content: `By uploading images (including profile avatars and company logos) to the Platform, you confirm that you have the right to use and share the content, and that it does not infringe the rights of any third party. Uploaded media is stored via Cloudinary and subject to their terms of service. Apex reserves the right to remove any uploaded content that violates these terms.`,
    },
    {
        title: '9. Disclaimer of Warranties',
        content: `The Platform is provided on an "as is" and "as available" basis without warranties of any kind, either express or implied. Apex does not warrant that the Platform will be uninterrupted, error-free, or free from harmful components. We reserve the right to modify, suspend, or discontinue the Platform at any time without notice.`,
    },
    {
        title: '10. Limitation of Liability',
        content: `To the fullest extent permitted by law, Apex shall not be liable for any indirect, incidental, special, consequential, or punitive damages arising from your use of or inability to use the Platform. Our total liability to you for any claim arising out of or relating to these terms or the Platform shall not exceed the amount you have paid to us in the twelve months preceding the claim.`,
    },
    {
        title: '11. Changes to Terms',
        content: `We reserve the right to modify these Terms and Conditions at any time. We will notify users of material changes by updating the date at the bottom of this page. Continued use of the Platform following any changes constitutes acceptance of the revised terms.`,
    },
    {
        title: '12. Governing Law',
        content: `These Terms and Conditions shall be governed by and construed in accordance with the laws of Ireland, without regard to its conflict of law provisions. Any disputes arising under or in connection with these terms shall be subject to the exclusive jurisdiction of the courts of Ireland.`,
    },
]

export function TermsPage() {
    return (
        <div className="min-h-dvh bg-grey-950 px-6 py-12 max-w-3xl mx-auto">
            <button
                type="button"
                onClick={() => window.history.back()}
                className="flex items-center gap-2 text-xs text-grey-500 hover:text-grey-200 transition-colors mb-10 cursor-pointer"
            >
                <ArrowLeft size={13} />
                Back
            </button>

            <div className="mb-10">
                <h1 className="text-3xl font-semibold text-grey-50 mb-3">Terms & Conditions</h1>
                <p className="text-xs text-grey-600">
                    Last updated:{' '}
                    {new Date().toLocaleDateString('en-IE', {
                        day: 'numeric',
                        month: 'long',
                        year: 'numeric',
                    })}
                </p>
            </div>

            <div className="flex flex-col gap-8">
                {SECTIONS.map(({ title, content }) => (
                    <div key={title}>
                        <h2 className="text-sm font-semibold text-grey-200 mb-2">{title}</h2>
                        <p className="text-xs text-grey-500 leading-relaxed">{content}</p>
                    </div>
                ))}
            </div>

            <div className="mt-12 pt-8 border-t border-grey-800">
                <p className="text-xs text-grey-700 text-center">
                    If you have questions about these Terms, contact us through the Platform.
                </p>
            </div>
        </div>
    )
}
