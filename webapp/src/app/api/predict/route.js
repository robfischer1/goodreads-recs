import getBooks from '@/app/api/_lib/db'

const TOP_N = 20

function createContext (data) {
  const bookIds = data.book_ids.slice(-10)
  const bookRatings = data.book_ratings.slice(-10)
  const padValues = (v) => v.concat(new Array(10 - v.length).fill(0))

  return [data.book_ids, {
    "inputs": {
      "context_id": padValues(bookIds),
      "context_rating": padValues(bookRatings)
    }
  }]
}

async function makePredictions (context) {
  return await fetch('http://serving:8501/v1/models/wrecksys:predict', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(context)
  })
    .then((response) => response.json())
    .then((results) => results['outputs']['recommendation_ids'])


//  return await tf.loadGraphModel('file://./assets/web_model/model.json')
//    .then((model) => model.predictAsync(context))
//    .then((results) => results[1].array())
}

export async function POST (request) {

  const results = await request.json()
    .then((data) => createContext(data))
    .then(async ([history, context]) => {
      const recs = await makePredictions(context)
      return recs.filter((x) => !history.includes(x)).slice(TOP_N)
    })
    .then((predictions) => getBooks({bookIds: predictions}))

  return new Response(JSON.stringify(results), {
    headers: { 'content-type': 'application/json' },
    status: 200
  })
}
