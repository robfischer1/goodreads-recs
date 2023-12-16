'use client'

import BooksContextProvider from '@/context/BooksContextProvider'
import WrecksContextProvider from '@/context/WrecksContextProvider'
import RatingsContextProvider from '@/context/RatingsContextProvider'
import ThemeRegistry from '@/context/ThemeRegistry/ThemeRegistry'

export default function ContextProviders ({ children }) {
  return (
    <ThemeRegistry>
      <BooksContextProvider>
        <RatingsContextProvider>
          <WrecksContextProvider>
            {children}
          </WrecksContextProvider>
        </RatingsContextProvider>
      </BooksContextProvider>
    </ThemeRegistry>
  )
}
