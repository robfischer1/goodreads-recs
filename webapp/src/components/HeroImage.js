import {Box, Button, Card, CardActions, CardContent, Typography} from '@mui/material'

export default function HeroImage () {
//                 background: "linear-gradient(to bottom, rgba(0, 0, 16, 1) 92%, rgba(0,0,16, .8) 100%)"
  return (
    <Box
      component='div'
      minHeight='100vh'
      height='100%'
      width='100%'
      bgcolor='#000010'
      position='relative'
    >
      <Box
        component='div'
        height='85vh'
        width='100%'
        sx={{
          backgroundImage: `
                    linear-gradient(to bottom, rgba(0, 0, 16, 0) 90%, rgba(0,0,16, 1) 100%), 
                    linear-gradient(to bottom right, rgba(0,0,16,0) 0%, rgba(0,0,16,.25) 70%, rgba(0,0,16,1) 100%), 
                    linear-gradient(to bottom left, rgba(0,0,16,0) 0%, rgba(0,0,16,.25) 70%, rgba(0,0,16,1) 100%), 
                    url(\"heroImage.png\")`,
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          backgroundSize: 'cover',
          position: 'relative'

        }}/>
      <Card
        elevation={0}
        sx={{
          background: 'none',
          position: 'absolute',
          right: '10vw',
          top: '60vh',
      }}>
        <CardContent>
          <Typography gutterBottom component="div" variant='h2' textAlign='center' color='white' sx={{ fontFamily: 'Shantell Sans' }}>
            But these are <em>awful!</em>
          </Typography>

          <Typography variant='body1' component='p' color='#8E8F86' sx={{ fontFamily: 'Open Sans', textAlign: 'justify', width: 0, minWidth: '100%' }}>
            Infinite monkeys will eventually produce the collected works of Shakespeare. But what if you only had one
            monkey? We decided to give ours a computer and ask him to write a recommendation system. How did he do?
          </Typography>
        </CardContent>
        <CardActions sx={{justifyContent: 'flex-end', border: 'none'}}>
          <Button size='large' variant='contained' color='tertiary' href='/books' sx={{fontWeight: 'bold'}}>
            Let&apos;s Find Out!
          </Button>
        </CardActions>
      </Card>
    </Box>
  )
}
