import { createSearchAppInit } from "@js/invenio_search_ui";
import {
    TDotDatEquilibriumSearchBarElement,
    TDotDatEquilibriumResultsGridItem,
    TDotDatEquilibriumResultsListItem
} from "./search_app_customizations";

const initSearchApp = createSearchAppInit({
  "ResultsList.item": TDotDatEquilibriumResultsListItem,
  "ResultsGrid.item": TDotDatEquilibriumResultsGridItem,
  "SearchBar.element": TDotDatEquilibriumSearchBarElement,
  "SearchApp.searchbarContainer": () => null,
});
