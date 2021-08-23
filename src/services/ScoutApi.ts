const axios = require('axios').default
const { BACKEND_URL } = process.env
const baseUrl = `${BACKEND_URL}/api/v1`

export const getAuthHeaders = () => ({
  headers: {
    Authorization: `Bearer ${document?.cookie},
    'Content-Type': 'application/json;charset=UTF-8',
    'Access-Control-Allow-Origin': '*'`,
  },
})

export const getInstituteFromURL = () => document?.location.pathname.split('/')[1]
export const getCaseFromURL = () => document?.location.pathname.split('/')[2]

export const getCases = async (): Promise<any> => {
  let response = { cases: [] }
  try {
    /* Test link, for more info: https://github.com/Clinical-Genomics/scout-mocks-data  */
    /* https://scout-mocks-data.herokuapp.com/cases */
    const request = await axios.get(`${baseUrl}/institutes/${getInstituteFromURL()}/cases`, {
      headers: getAuthHeaders(),
      withCredentials: true,
    })
    response = request.data
  } catch (error) {
    console.error(error)
  }
  return response
}

export const getCaseReport = async (): Promise<any> => {
  let response = { report: [] }

  try {
    /* Test link, for more info: https://github.com/Clinical-Genomics/scout-mocks-data  */
    /* https://scout-mocks-data.herokuapp.com/case_report */
    const request = await axios.get(`${baseUrl}/institutes/${getInstituteFromURL()}/case_report`, {
      headers: getAuthHeaders(),
      withCredentials: true,
    })
    response = await request.json()
  } catch (error) {
    console.error(error)
  }
  return response
}
