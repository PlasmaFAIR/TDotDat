import { createSearchAppInit } from "@js/invenio_search_ui";
import {
  TDotDatSearchBarElement,
  TDotDatResultsListItem,
  TDotDatResultsGridItem,
 } from "./search_app_customizations";

const initSearchApp = createSearchAppInit({
  "ResultsList.item": TDotDatResultsListItem,
  "ResultsGrid.item": TDotDatResultsGridItem,
  "SearchBar.element": TDotDatSearchBarElement,
  "SearchApp.searchbarContainer": () => null,
});
