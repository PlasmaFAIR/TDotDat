/*
 * A search bar for finding the PID of an equilibrium
 *
 *   Copyright (C) 2022 TDoTP.
 *
 * TDotDat is free software; you can redistribute it and/or modify it under
 * the terms of the MIT License; see LICENSE file for more details.
 */

import React, { Component } from 'react'
import { Container, Search, Grid, Header, Segment, FormField } from 'semantic-ui-react'
import axios from 'axios';

// Default initial state for search bar
const initialState = {
  loading: false,
  results: [],
  value: '',
  cancelToken: ''
}

// Enables moving state/logic mapping out of main EquilibriumSelection
function reducer(state, action) {
  switch (action.type) {
  case 'CLEAN_QUERY':
    return initialState
  case 'START_SEARCH':
    return { ...state, loading: true, value: action.query, cancelToken: action.token }
  case 'FINISH_SEARCH':
    return { ...state, loading: false, results: action.results }
  case 'UPDATE_SELECTION':
    return { ...state, value: action.selection }

  default:
    throw new Error()
  }
}

// Renderer for each individual search result in the dropdown
// selection box
const resultRenderer = (result) => (
  <div key='content' className='content'>
    {result.title && <div className='title'>{result.title}</div>}
    {result.pid && <div className='id'>ID: {result.pid}</div>}
    {result.elongation && <div className='elongation'>elongation: {result.elongation}</div>}
    {result.q && <div className='q'>q: {result.q}</div>}
    {result.B0 && <div className='B0'>B0: {result.B0}</div>}
  </div>
)

// Allow the user to search for and choose an equilibrium without
// knowing its ID
function EquilibriumSelection() {

  // Get a dispatcher to advance the state, along with all the
  // components of the current state
  const [state, dispatch] = React.useReducer(reducer, initialState);
  const { loading, results, value, cancelToken } = state

  // Gives us some mutable state that lasts for the lifetime of the component
  const timeoutRef = React.useRef();

  // Our actual search function
  const search = React.useCallback((e, data) => {
    clearTimeout(timeoutRef.current);
    // cancel any previous request in case it is still happening
    cancelToken && cancelToken.cancel();
    // generate a new cancel token for this request
    const cancelToken = axios.CancelToken.source();

    // Start the search, updating the text in the search box
    dispatch({ type: 'START_SEARCH', query: data.value, token: cancelToken });

    // Encode what the user types into something suitable to be passed
    // to the REST API
    const params = new URLSearchParams();
    params.append("q", data.value);

    // Gives us a little bit of a delay between the user typing and
    // the search running (delay is in milliseconds)
    const delay = 300;
    timeoutRef.current = setTimeout(() => {
      // Don't bother searching if there's no input!
      if (data.value.length === 0) {
        dispatch({ type: 'CLEAN_QUERY' })
        return
      }

      // Now we actually make our REST API call
      axios
        .get("/api/equilibrium/", {
          params: params,
          cancelToken: cancelToken.token,
        })
        .then(function (response) {
          // We've got something, we just need to unwrap the array of metadata
          dispatch({
            type: "FINISH_SEARCH",
            results: response.data.hits.hits.map((item) => ( item.metadata ))
          })
        })
        .catch(function (error) { console.log(error) })
    }, delay)
  }, []);

  React.useEffect(() => {
    return () => {
      clearTimeout(timeoutRef.current)
    }
  }, []);

  return (
    <FormField>
      <label htmlFor="equilibrium_id">Equilibrium ID</label>
      <Search
        name="equilibrium_id"
        fluid
        loading={loading}
        placeholder='Search for an equilibrium...'
        onResultSelect={(e, data) =>
          dispatch({ type: 'UPDATE_SELECTION', selection: data.result.pid })
        }
        onSearchChange={search}
        results={results}
        resultRenderer={resultRenderer}
        value={value}
      />
    </FormField>
  );
}

export default EquilibriumSelection;
