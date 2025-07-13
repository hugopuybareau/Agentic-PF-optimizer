import { Navigation } from '@/components/Navigation'

export default function Contact() {
  return (
    <div className="min-h-screen bg-background">
      <Navigation />
      
      <main className="pt-20 px-6 pb-12">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-hero mb-4">Get in touch</h1>
            <p className="text-sub">Have questions? We'd love to hear from you.</p>
          </div>

          <div className="grid lg:grid-cols-2 gap-12">
            {/* Contact Form */}
            <div className="card-platine p-8 rounded-lg">
              <h2 className="text-nav font-semibold mb-6">Send us a message</h2>
              
              <form className="space-y-6">
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sub text-sm mb-2">First name</label>
                    <input
                      type="text"
                      className="w-full px-4 py-3 bg-input border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 text-nav"
                      placeholder="John"
                    />
                  </div>
                  <div>
                    <label className="block text-sub text-sm mb-2">Last name</label>
                    <input
                      type="text"
                      className="w-full px-4 py-3 bg-input border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 text-nav"
                      placeholder="Doe"
                    />
                  </div>
                </div>
                
                <div>
                  <label className="block text-sub text-sm mb-2">Email</label>
                  <input
                    type="email"
                    className="w-full px-4 py-3 bg-input border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 text-nav"
                    placeholder="john@example.com"
                  />
                </div>
                
                <div>
                  <label className="block text-sub text-sm mb-2">Subject</label>
                  <input
                    type="text"
                    className="w-full px-4 py-3 bg-input border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 text-nav"
                    placeholder="How can we help?"
                  />
                </div>
                
                <div>
                  <label className="block text-sub text-sm mb-2">Message</label>
                  <textarea
                    rows={6}
                    className="w-full px-4 py-3 bg-input border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 text-nav resize-none"
                    placeholder="Tell us more about your inquiry..."
                  />
                </div>
                
                <button
                  type="submit"
                  className="w-full btn-primary px-6 py-3 rounded-lg text-nav"
                >
                  Send Message
                </button>
              </form>
            </div>

            {/* Contact Info */}
            <div className="space-y-8">
              <div className="card-platine p-8 rounded-lg">
                <h2 className="text-nav font-semibold mb-6">Contact Information</h2>
                
                <div className="space-y-6">
                  <div className="flex items-start space-x-4">
                    <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center mt-1">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                    </div>
                    <div>
                      <h3 className="text-nav font-medium">Email</h3>
                      <p className="text-sub">hello@platine.ai</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-4">
                    <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center mt-1">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                    </div>
                    <div>
                      <h3 className="text-nav font-medium">Location</h3>
                      <p className="text-sub">San Francisco, CA</p>
                    </div>
                  </div>
                  
                  <div className="flex items-start space-x-4">
                    <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center mt-1">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div>
                      <h3 className="text-nav font-medium">Response Time</h3>
                      <p className="text-sub">Within 24 hours</p>
                    </div>
                  </div>
                </div>
              </div>

              <div className="card-platine p-8 rounded-lg">
                <h2 className="text-nav font-semibold mb-6">Frequently Asked</h2>
                
                <div className="space-y-4">
                  <div>
                    <h3 className="text-nav font-medium mb-2">How secure is my data?</h3>
                    <p className="text-sub text-sm">We use bank-level encryption and never store your login credentials.</p>
                  </div>
                  
                  <div>
                    <h3 className="text-nav font-medium mb-2">Is there a free trial?</h3>
                    <p className="text-sub text-sm">Yes, get started with a 14-day free trial. No credit card required.</p>
                  </div>
                  
                  <div>
                    <h3 className="text-nav font-medium mb-2">Can I cancel anytime?</h3>
                    <p className="text-sub text-sm">Absolutely. Cancel your subscription at any time with no penalties.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}