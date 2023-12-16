import sqlite3 from 'sqlite3'
import {open} from 'sqlite'

const PAGE_SIZE = 10

const upscaleImages = (books) => books.map(book => ({ ...book, image_url: book.image_url.replace(/(?<=\d)m/m, 'l') }))
const getIndex = (i) => 1 + (i - 1) * PAGE_SIZE
const makeQueryStr = (n) => new Array(n).fill('?').join(',')

export default async function getBooks({page, bookIds}){
  const con = await open({
    filename: './assets/app.db',
    driver: sqlite3.Database
  })

  try {
    if (page && bookIds) {
      throw new TypeError("Pick one, champ.")
    }
    if (!page && !bookIds) {
      throw new TypeError("getBooks() requires at least one argument.")
    }
    const cols = 'work_index, book_id, title, author_name, link, image_url'

    const query = page ?
      await con.all(`SELECT ${cols} FROM books WHERE work_index >= ? LIMIT ?`, [getIndex(page), PAGE_SIZE])
      : await con.all(`SELECT ${cols} FROM books WHERE work_index IN (${makeQueryStr(bookIds.length)})`, bookIds)

    return upscaleImages(query)

  } finally {
    await con.close()
  }


}
