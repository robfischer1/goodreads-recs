'use client'

import {Fragment, useContext, useEffect, useMemo, useRef} from 'react'
import BookGrid from '@/components/BookGrid'
import {Box, Fab, Typography, useMediaQuery, useTheme} from '@mui/material'
import Button from '@mui/material/Button'
import SyncIcon from '@mui/icons-material/Sync'
import {RatingsContext} from '@/context/RatingsContextProvider'
import {BooksContext} from '@/context/BooksContextProvider'
import {WrecksContext} from '@/context/WrecksContextProvider'
import {useRouter} from 'next/navigation'
import {RexIcon} from "@/components/RexIcon";
import Container from "@mui/material/Container";

function ResetButton ({ callbackFn }) {
  return (
    <Box right={0} sx={{ display: 'flex', justifyContent: 'flex-end', mb: 1 }}>
      <Button
        variant='contained'
        endIcon={<SyncIcon />}
        onClick={() => callbackFn()}
        sx={{borderRadius: 3}}
      >
        Reset
      </Button>
    </Box>
  )
}

function PredictButton ({ wrecks, setWrecks, userData }) {
  const router = useRouter()
  const theme = useTheme()
  const displayLabel = useMediaQuery(theme.breakpoints.up('sm'));
  const handleOnClick = async () => {
    console.log(JSON.stringify(userData))
    if (userData.book_ids.length === 0) return;

    await fetch('/api/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(userData)

    })
      .then((response) => response.json())
      .then((json) => setWrecks(json))
      .then(() => console.log(JSON.stringify(wrecks)))
      .finally(() => {
        console.log("What, why?")
        router.push('/books/suggest')
      })
  }

  return (
    <Fab
      variant={displayLabel ? 'extended' : 'circular'}
      color='tertiary'
      onClick={() => handleOnClick()}
      title="Recommendations"
      sx={{
        position: 'fixed',
        bottom: 25,
        right: 25,
        ':hover': {
          backgroundColor: 'tertiary.contrastText',
          color: 'tertiary.main'
        },
      }}
    >
      <RexIcon sx={{fontSize: 40, pr: {sm: 0, md: 1}}}/>
      {displayLabel ? "Get Recommendations" : ""}
    </Fab>
  )
}

export default function Books () {
  const { books, loadNext } = useContext(BooksContext)
  const { ratings, setRatings } = useContext(RatingsContext)
  const { wrecks, setWrecks } = useContext(WrecksContext)
  const bottom = useRef(null)

  const userRatings = useMemo(() => {
    return { book_ids: [...ratings.keys()], book_ratings: [...ratings.values()] }
  }, [ratings])

  const resetRatings = () => {
    setWrecks([])
    setRatings(new Map())
    console.log(wrecks)
    console.log(ratings)
  }

  useEffect(() => {
    let lastRef = null
    const observer = new IntersectionObserver((entries) => {
      const target = entries[0]
      if (target.isIntersecting) {
        loadNext()
      }
    })

    if (bottom.current) {
      observer.observe(bottom.current)
      lastRef = bottom.current
    }

    return () => {
      if (lastRef) {
        observer.unobserve(lastRef)
      }
    }
  }, [loadNext])

  return (
    <Container sx={{ py: 16 }} maxWidth='md'>
      <Typography component="div" variant="h5" color="primary" sx={{fontWeight: 'bold'}}>Rate some books to get started.</Typography>
      <ResetButton callbackFn={resetRatings} />
      <BookGrid books={books} />
      <div id='bottom' ref={bottom} />
      <PredictButton wrecks={wrecks} setWrecks={setWrecks} userData={userRatings} />
    </Container>
  )
};
