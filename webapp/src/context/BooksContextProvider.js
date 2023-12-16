'use client'

import {createContext, useCallback, useEffect, useMemo, useState} from 'react'

export const BooksContext = createContext(null)

export default function BooksContextProvider ({ children }) {
  const [books, setBooks] = useState([])
  const [pageNum, setPageNum] = useState(2)
  const [loading, setLoading] = useState(false)

  const loadPage = async (n) => {
    return await fetch(`/api/books?page=${n}`)
      .then((res) => res.json())
  }

  const loadNext = useCallback(async () => {
    if (loading) return;

    setLoading(true)
    await loadPage(pageNum)
      .then((data) => setBooks((prevBooks) => [...prevBooks, ...data]))
      .then(() => setPageNum((prevPage) => prevPage + 1))
      .finally(() => setLoading(false))

  }, [loading, pageNum])

  useEffect(() => {
    const loadFirst = async () => {
      setLoading(true)
      await loadPage(1)
        .then((data) => setBooks([...data]))
        .finally(() => setLoading(false))
    }
    void loadFirst()
  }, []);

  const val = useMemo(() => ({
    books,
    loadNext
  }), [books, loadNext])

  return (
    <BooksContext.Provider value={val}>
      {children}
    </BooksContext.Provider>
  )
}
