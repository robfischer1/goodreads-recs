import getBooks from '@/app/api/_lib/db'

export async function GET (request) {

  const pageNo = request.nextUrl.searchParams.get('page') || 1
  const books = await getBooks({page: pageNo})

  return new Response(JSON.stringify(books), {
    headers: { 'content-type': 'application/json' },
    status: 200
  })
}
