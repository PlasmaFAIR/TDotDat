import { createSearchAppInit } from "@js/invenio_search_ui";
import {
  TDotDatSearchBarElement,
  TDotDatResultsListItem,
  TDotDatResultsGridItem,
  TDotDatSearchBarContainer,
  TDotDatValueElement
 } from "./search_app_customizations";

const initSearchApp = createSearchAppInit({
  "ResultsList.item": TDotDatResultsListItem,
  "ResultsGrid.item": TDotDatResultsGridItem,
  "SearchBar.element": TDotDatSearchBarElement,
  "SearchApp.searchbarContainer": TDotDatSearchBarContainer,
  "BucketAggregationValues.element": TDotDatValueElement
});
