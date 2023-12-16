import {Box} from '@mui/material'
import Container from '@mui/material/Container'
import Typography from "@mui/material/Typography";
import Grid from "@mui/material/Unstable_Grid2";

export function LabelText({ text, bottom }) {

  return (
    <Typography
      paragraph={true}
      variant="h4"
      sx={{
        fontFamily: "'Shantell Sans', cursive",
        backgroundColor: '#FFF',
        border: 'solid 2px #000',
        margin: 0,
        padding: '3px 10px',
        ...(bottom ? {
            position: 'absolute',
            bottom: '-2px',
            right: '-6px',
            transform: 'skew(-15deg)'
          } :
          {
            position: 'absolute',
            top: '-2px',
            left: '-6px',
            transform: 'skew(-15deg)'
          })
      }}>
      {text}
    </Typography>
  )
}

export function StoryPanel({image, breakpoints, props, topText, bottomText}) {

  return (
    <Grid {...breakpoints}>
      <Box
        display="inline-block"
        sx={{
          overflow: 'hidden',
          position: 'relative',
          border: 'solid 2px #000',
          boxShadow: '0 6px 6px -6px #000',
          width: '100%',
          backgroundImage: `url(${image})`,
          backgroundPosition: 'top',
          backgroundRepeat: 'no-repeat',
          backgroundSize: 'cover',
          ...({...props})
        }}>
        {topText && <LabelText text={topText} />}
        {bottomText && <LabelText text={bottomText} bottom/>}
      </Box>
    </Grid>
  )

}

export default function Storyboard () {
  const panels = [
    {
      image: 'friendly-monkey.png',
      breakpoints: {xs:12, md: 6},
      props: {aspectRatio: 1, backgroundPosition: 'top'},
      topText: 'Meet Rex...',
      bottomText: "...he makes recommendations."
    },
    {
      image: 'gorilla-fruit.png',
      breakpoints: {xs:12, md: 6},
      props: {aspectRatio: 1, backgroundPosition: 'top'},
      topText: 'This is George.',
      bottomText: "George likes fruit."
    },
    {
      image: 'thinking-monkey.png',
      breakpoints: {xs:12, md: 6},
      props: {aspectRatio: 1, backgroundPosition: 'top'},
      topText: 'Who else likes fruit?'
    },
    {
      image: 'child-fruit.png',
      breakpoints: {xs:12, md: 6},
      props: {aspectRatio: 1, backgroundPosition: 'top'},
      bottomText: "Children like fruit."
    },
    {
      image: 'excited-monkey.png',
      breakpoints: {xs:12, md: 6},
      props: {aspectRatio: 1, backgroundPosition: 'top'},
    },
    {
      image: 'child-games.png',
      breakpoints: {xs:12, md: 6},
      props: {aspectRatio: 1, backgroundPosition: 'top'},
      topText: 'What else do children like?',
      bottomText: "Video Games!"
    },
    {
      image: 'gorilla-box.png',
      breakpoints: {xs:12},
      props: {aspectRatio: 1.5, backgroundPosition: 'center'},
      topText: 'Those are perfect for George!',
    },
    {
      image: 'games-box.png',
      breakpoints: {xs:12},
      props: {aspectRatio: 3, backgroundPosition: 'top'},
    },
    {
      image: 'gorilla-confused.png',
      breakpoints: {xs:12, md: 6},
      props: {aspectRatio: 1, backgroundPosition: 'top'},
      bottomText: "George is not amused."
    },
    {
      image: 'sad-monkey.png',
      breakpoints: {xs:12, md: 6},
      props: {aspectRatio: 1, backgroundPosition: 'top'},
      topText: 'Rex?',
      bottomText: "Well, he's bad at this."
    },
    {
      image: 'midjourney.png',
      breakpoints: {xs:12},
      props: {aspectRatio: 1.5, backgroundPosition: 'top'},
      topText: "Me? I'm Rob",
      bottomText: "I'm not an artist, but MidJourney is wild."
    },
  ]

  return (
    <Container maxWidth={'xl'} sx={{mt: 10}}>
      <Grid container spacing={1} margin={1}>
        {panels.map((panel, i) => (
          <StoryPanel key={i} {...panel} />
        ))};
      </Grid>
    </Container>
  )
}
