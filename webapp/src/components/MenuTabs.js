'use client'

import {useEffect, useState} from 'react'
import {Box, IconButton, Menu, MenuItem, Tab, Tabs} from '@mui/material'
import {usePathname, useRouter} from 'next/navigation'
import Typography from '@mui/material/Typography'
import MenuIcon from '@mui/icons-material/Menu'

const pages = {
  '/': { index: 0, title: 'Home', href: '/' },
  '/about': { index: 1, title: 'About', href: '/about' },
  '/books': { index: 2, title: 'Books', href: '/books' },
  '/books/suggest': { index: 3, title: 'Suggestions', href: '/books/suggest' },
  '/capstone': { index: 4, title: 'Capstone', href: 'https://colab.research.google.com/github/robfischer1/goodreads-recs/blob/master/Capstone.ipynb' }
}

export function MenuHidden () {
  const menuRouter = useRouter()

  const [anchorElNav, setAnchorElNav] = useState(null)

  const handleOpenNavMenu = (event) => {
    setAnchorElNav(event.currentTarget)
  }

  const handleCloseNavMenu = () => {
    setAnchorElNav(null)
  }

  const handleOnClick = (url) => {
    menuRouter.push(url)
    setAnchorElNav(null)
  }

  return (
    <Box sx={{ display: { xs: 'flex', md: 'none' } }}>
      <IconButton
        size='large'
        aria-label='Menu'
        aria-controls='menu-appbar'
        aria-haspopup='true'
        onClick={handleOpenNavMenu}

      >
        <MenuIcon sx={{ fontSize: 30 }} />
      </IconButton>
      <Menu
        id='menu-appbar'
        anchorEl={anchorElNav}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'left'
        }}
        keepMounted
        transformOrigin={{
          vertical: 'top',
          horizontal: 'left'
        }}
        open={Boolean(anchorElNav)}
        onClose={handleCloseNavMenu}
        sx={{
          display: { xs: 'block', md: 'none' }
        }}
      >
        {Object.keys(pages).map((p) => (
          <MenuItem key={pages[p].index} href={pages[p].href} onClick={(e) => handleOnClick(pages[p].href)}>
            <Typography textAlign='center'>
              {pages[p].title}
            </Typography>
          </MenuItem>
        ))}
      </Menu>
    </Box>
  )
}

export function MenuTabs () {
  const router = useRouter()
  const path = usePathname()

  const [tab, setTab] = useState(0)

  const pageRouter = (e, newPage) => {
    e.preventDefault()
    router.push(e.target.href)
  }

  const changeTab = (e, newTab) => {
    setTab(newTab)
  }

  useEffect(() => {
    setTab(pages[path].index)
  }, [path])

  return (
    <Tabs
      value={tab}
      onChange={changeTab}
      scrollButtons={false}
      aria-label='navpanel'
      sx={{
        alignSelf: 'flex-end',
        justifySelf: 'flex-end',
        display: { xs: 'none', md: 'flex' },
        justifyContent: 'flex-end',
      }}
    >
      {Object.keys(pages).map((p) => (
        <Tab
          component='a'
          key={pages[p].index}
          id={`tab-${pages[p].index}`}
          label={pages[p].title}
          href={pages[p].href}
          onClick={(e) => pageRouter(e)}
          sx={{
            fontSize: '1rem',
          }}
        />
      ))}
    </Tabs>
  )
}
