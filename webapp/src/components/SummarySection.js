import {Box, Typography} from "@mui/material";
import Container from "@mui/material/Container";
import Grid from "@mui/material/Unstable_Grid2";
import {DoneAllRounded, ScienceRounded, StarHalfRounded} from "@mui/icons-material";
import {RexIcon} from "@/components/RexIcon";

export default function SummarySection() {
  return (
    <Box sx={{
      width: '100%',
      display: 'block',
      background: '#3d4557',
      py: 10,
    }}>
      <Container sx={{}} maxWidth='lg'>
        <Grid container sx={{justifyContent: 'space-evenly'}} spacing={{sm: 3, md: 4}}>
          <Grid xs={12} sx={{textAlign: 'center'}}>
            <Typography color='white' component="div" variant="h4" sx={{margin: 'auto', fontWeight: 600}}>How It Works</Typography>
          </Grid>
          <Grid xs={12} sm={3} sx={{textAlign: 'center', mt: 3}}>
            <StarHalfRounded sx={{fontSize: 80, color: 'white'}}/>
            <Typography color='white' component="div" variant="h6" sx={{margin: 'auto'}}>Rate Books</Typography>
            <Typography color='silver' component="p" variant="body" sx={{margin: 'auto', width: 0, minWidth: '100%'}}>Pick from over 20,000 titles.</Typography>
          </Grid>
          <Grid xs={12} sm={3} sx={{textAlign: 'center', mt: 3}}>
            <RexIcon sx={{fontSize: 80, color: 'white'}}/>
            <Box>
            <Typography color='white' component="div" variant="h6" sx={{margin: 'auto'}}>Ask Rex</Typography>
            <Typography color='lightgray' component="p" variant="body" sx={{margin: 'auto', width: 0, minWidth: '100%'}}>The sad thing is, Rex is as good at this as most AI startups.</Typography>
            </Box>
          </Grid>
          <Grid xs={12} sm={3} sx={{textAlign: 'center', mt: 3}}>
            <ScienceRounded sx={{fontSize: 80, color: 'white'}}/>
            <Box>
            <Typography color='white' component="div" variant="h6" sx={{margin: 'auto'}}>Get Recommendations</Typography>
            <Typography color='lightgray' component="p" variant="body" sx={{margin: 'auto', width: 0, minWidth: '100%'}}>They&apos;re pretty terrible.</Typography>
            </Box>
          </Grid>
          <Grid xs={12} sm={3} sx={{textAlign: 'center', mt: 3}}>
            <DoneAllRounded sx={{fontSize: 80, color: 'white'}}/>
            <Box>
            <Typography color='white' component="div" variant="h6" sx={{margin: 'auto'}}>That&apos;s it!</Typography>
            <Typography color='lightgray' component="p" variant="body" sx={{margin: 'auto', width: 0, minWidth: '100%'}}>For how long this took, you&apos;d think it did more.</Typography>
            </Box>
          </Grid>
        </Grid>
      </Container>

    </Box>
  )
}
