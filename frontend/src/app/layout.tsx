import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Ultron Empire — PMS Sahi Hai',
  description: "India's 1st AI Powered PMS & AIF Marketplace Dashboard",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-brand-light-bg">
        <nav className="bg-brand-deep-teal text-white px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-brand-emerald rounded-full flex items-center justify-center font-bold text-sm">N</div>
            <div>
              <h1 className="text-lg font-semibold">Ultron Empire</h1>
              <p className="text-xs text-brand-mint opacity-80">PMS Sahi Hai</p>
            </div>
          </div>
          <div className="flex gap-6 text-sm">
            <a href="/" className="hover:text-brand-mint">Dashboard</a>
            <a href="/chat" className="hover:text-brand-mint">Chat</a>
            <a href="/clients" className="hover:text-brand-mint">Clients</a>
            <a href="/market" className="hover:text-brand-mint">Market</a>
            <a href="/alerts" className="hover:text-brand-mint">Alerts</a>
            <a href="/predictions" className="hover:text-brand-mint">Signals</a>
            <a href="/analytics" className="hover:text-brand-mint">Analytics</a>
          </div>
        </nav>
        <main className="p-6">{children}</main>
      </body>
    </html>
  );
}
