'use client'

import {createContext, useEffect, useMemo, useState} from 'react'
import {delStorage, getStorage, setStorage} from '@/context/storage'

export const RatingsContext = createContext(null)

function initialState () {
  const savedRatings = getStorage('ratings')
  if (savedRatings) {
    return new Map(savedRatings)
  }
  return new Map()
}

function saveState (currentState) {
  const arr = Array.from(currentState.entries())
  if (arr.length > 0) {
    setStorage('ratings', arr)
  } else {
    delStorage('ratings')
  }
}

export default function RatingsContextProvider ({ children }) {
  const [ratings, setRatings] = useState(initialState())
  useEffect(() => {
    saveState(ratings)
  }, [ratings])

  const val = useMemo(() => ({
    ratings,
    setRatings
  }), [ratings]
  )

  return (
    <RatingsContext.Provider value={val}>
      {children}
    </RatingsContext.Provider>
  )
}
