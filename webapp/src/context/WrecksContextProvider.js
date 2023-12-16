'use client'

import {createContext, useEffect, useMemo, useState} from 'react'
import {delStorage, getStorage, setStorage} from '@/context/storage'

export const WrecksContext = createContext(null)

function initialState () {
  const savedWrecks = getStorage('wrecks')
  return savedWrecks || []
}

function saveState (currentState) {
  if (currentState.length > 0) {
    setStorage('wrecks', currentState)
  } else {
    delStorage('wrecks')
  }
}

export default function WrecksContextProvider ({ children }) {
  const [wrecks, setWrecks] = useState(initialState())
  useEffect(() => {
    saveState(wrecks)
  }, [wrecks])

  const val = useMemo(() => ({
    wrecks,
    setWrecks
  }), [wrecks]
  )

  return (
    <WrecksContext.Provider value={val}>
      {children}
    </WrecksContext.Provider>
  )
}
