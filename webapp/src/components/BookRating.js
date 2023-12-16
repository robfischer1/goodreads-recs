'use client'

import {useContext, useEffect, useMemo, useState} from 'react'
import {RatingsContext} from '@/context/RatingsContextProvider'
import {Rating} from '@mui/material'

export default function BookRating ({ bookID }) {
  const { ratings, setRatings } = useContext(RatingsContext)
  const prevRating = useMemo(() => {
    return ratings.get(bookID) === undefined ? null : ratings.get(bookID)
  }, [bookID, ratings])
  const [val, setVal] = useState(prevRating)
  const handleChange = (e, rating) => {
    setVal(rating)
    if (rating) {
      setRatings((prev) => new Map(prev.set(bookID, rating)))
    } else {
      ratings.delete(bookID)
    }
  }

  useEffect(() => {
    setVal(prevRating)
  }, [prevRating])

  return (
    <Rating
      size='large'
      sx={{ mx: 'auto' }}
      value={val}
      onChange={handleChange}
    />
  )
}
