import Card from '@mui/material/Card'
import CardMedia from '@mui/material/CardMedia'
import Typography from '@mui/material/Typography'
import CardActions from '@mui/material/CardActions'
import * as React from 'react'
import Link from '@mui/material/Link'
import BookRating from '@/components/BookRating'
import Tooltip from '@mui/material/Tooltip'
import Grid from '@mui/material/Unstable_Grid2'
import {Avatar, Box, CardContent, Chip, List, ListItem} from "@mui/material";
import Container from "@mui/material/Container";

const titleRegex = /(.+) \((.+)\)/m
const splitTitle = (title) => {
  const titleParts = titleRegex.exec(title)
  return [
    titleParts ? titleParts[1] : title,
    titleParts ? titleParts[2] : ' '
  ]
}

export function CoverCard ({ book }) {
  const [bookTitle, bookSeries] = splitTitle(book.title)

  return (
    <Card
      component='div'
      sx={{
        width: '100%',
        aspectRatio: '3 / 5',
        display: 'flex',
        flexDirection: 'column'
      }}
    >
      <CardMedia
        component='div'
        sx={{
          height: '100%',
          size: 'contain',
          backgroundImage: `
                      linear-gradient(to bottom, rgba(255, 255, 255, 0) 95%, rgba(255, 255, 255, 1) 100%),
                      url(${book.image_url})`,
          backgroundPosition: '0% 0%',
          ':hover .overlay': {
            display:'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            backgroundColor:'black',
            opacity: 0.75
          }
        }}
        >
        <Box className="overlay" sx={{ position: "relative", width: "100%", height: "100%", display: "none", p: 2}}>
          <Link
            href={book.link}
            title={book.title}
            target='_blank'
            rel='noopener noreferrer'
          >
            <Typography variant='body1' color='white' sx={{mb: 1}}>
              {bookTitle}
            </Typography>
          </Link>
          <Typography variant='subtitle2' color='white' noWrap>
            {bookSeries}&nbsp;
          </Typography>
          <Typography variant='subtitle1' color='white'>
            by {book.author_name}
          </Typography>
        </Box>
      </CardMedia>
      <CardActions sx={{ mx: 'auto', my: 0, pt: 0, pb: 0.5, width: '100%' }}>
        <BookRating bookID={book.work_index} />
      </CardActions>
    </Card>
  )
}

export function DetailsCard ({ book }) {
  const [bookTitle, bookSeries] = splitTitle(book.title)

  return (
    <Card sx={{display: 'flex', height: 200}}>
      <CardMedia
        component='div'
        sx={{
          display: 'flex',
          height: '100%',
          aspectRatio: '3 / 5',
          borderRadius: 1,
          backgroundImage: `url(${book.image_url})`,
          backgroundSize: 'cover',
          backgroundPosition: 'center'
        }}
      />
      <Box sx={{display: 'flex', flexDirection: 'column', pl: 1, justifyContent: 'center'}}>
        <CardContent sx={{ flex: '1 0 auto'}}>
          <Typography component="div" variant="overline" color="text.secondary">
            {bookSeries}
          </Typography>
          <Typography component="div" variant="h5">
            {bookTitle}
          </Typography>
          <Typography component="div" variant="subtitle1" color="text.secondary">
            {book.author_name}
          </Typography>
        </CardContent>
        <Box sx={{display: 'flex', alignItems: 'center', p: 1}}>
          <Chip
            avatar={<Avatar src="/goodreads.ico" />}
            label="View on Goodreads"
            component="a"
            href={`https://www.goodreads.com/book/show/${book.book_id}`}
            variant="outlined"
            size="small"
            clickable />
          <Chip
            avatar={<Avatar src="/amazon.ico" />}
            size="small"
            label="Buy on Amazon"
          />
        </Box>
      </Box>
    </Card>
  )
}

export function BookList({ books }) {

  return (
      <Grid container spacing={1}>
        {books.map((book) => (
          <Grid key={book.work_index} xs={12} lg={6}>
            <DetailsCard book={book} />
          </Grid>
        ))}
      </Grid>
  )
}

export default function BookGrid ({ books }) {
  return (
      <Grid container spacing={1}>
        {books.map((book) => (
          <Grid key={book.work_index} xs={6} sm={4} md={3}>
            <CoverCard book={book} />
          </Grid>
        ))}
      </Grid>
  )
}
