import {AppBar, Box, Toolbar} from '@mui/material'
import {MenuHidden, MenuTabs} from '@/components/MenuTabs'

export default function FloatingNav () {
  return (
    <AppBar elevation={24} sx={{ mx: 0, px: 1, pb: 0, backgroundColor: 'white' }}>
      <Toolbar sx={{ height: 50, minHeight: 50, mb: 0, pb: 0, alignItems: 'center', justifyContent: 'space-between' }} disableGutters>
        <Box
          component='img'
          sx={{
            height: 40,
            width: 240,
            p: 0.25,
            pl: 0.25,
            justifySelf: 'flex-start',
          }}
          alt='Wrecksys Logo'
          src='/wrecksysLogo.svg'
        />
        <MenuTabs />
        <MenuHidden />
      </Toolbar>
    </AppBar>
  )
}
