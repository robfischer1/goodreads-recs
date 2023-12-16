import FloatingNav from '@/components/FloatingNav'
import ContextProviders from '@/context/ContextProviders'

export const metadata = {
  title: 'WreckSys',
  description: 'The home of truly terrible recommendations.'
}

export default function RootLayout ({ children }) {
  return (
    <html lang='en'>
      <body>
        <ContextProviders>
          <FloatingNav />
          {children}
        </ContextProviders>
      </body>
    </html>
  )
}
