'use client'

import {BookList} from '@/components/BookGrid'
import {useContext} from 'react'
import {WrecksContext} from '@/context/WrecksContextProvider'
import {Card, CardContent, CardMedia, Fab, Typography, useMediaQuery, useTheme} from "@mui/material";
import Container from "@mui/material/Container";
import {useRouter} from "next/navigation";
import {KeyboardDoubleArrowLeft} from "@mui/icons-material";

function BackButton () {
  const router = useRouter()
  const theme = useTheme()
  const displayLabel = useMediaQuery(theme.breakpoints.up('sm'));

  return (
    <Fab
      variant={displayLabel ? 'extended' : 'circular'}
      color='primary'
      onClick={() => router.push('/books')}
      title="Back"
      sx={{
        position: 'fixed',
        bottom: 25,
        right: 25,
        ':hover': {
          backgroundColor: 'primary.contrastText',
          color: 'primary.main'
        },
      }}
    >
      <KeyboardDoubleArrowLeft sx={{fontSize: 40, pr: {sm: 0, md: 1}}}/>
      {displayLabel ? "Back to Books" : ""}
    </Fab>
  )
}

export default function Suggest () {
  const { wrecks, _ } = useContext(WrecksContext)

  return (
    <Container sx={{ py: 16 }} maxWidth='lg'>
      {wrecks.length > 0 ?
      <BookList books={wrecks} />
        : <Card sx={{maxWidth: 300, margin: 'auto', borderRadius: 2}}>
            <CardMedia
              sx={{height: 300, backgroundSize: "contain"}}
              image="SadRex.jpg"
            />
            <CardContent>
              <Typography variant="h6">Please rate some books first.</Typography>
            </CardContent>
        </Card>}
      <BackButton />
    </Container>
  )
}
