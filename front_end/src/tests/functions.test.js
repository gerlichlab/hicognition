import {
    argsort,
    sort_matrix_by_index,
    sort_matrix_by_center_column,
    max_array,
    min_array,
    normalizeLineProfile,
    interQuartileRange,
    getQuartile,
    getPercentile
} from "../functions.js";
import { toBeDeepCloseTo } from "jest-matcher-deep-close-to";

// add deep comparison for arrays containing floats
expect.extend({ toBeDeepCloseTo });

// test argsort

describe("Argsort testing suite", function() {
    it("Test ascending argsort unordered array", () => {
        expect(argsort([4, 2, 6, 1, 3])).toEqual([3, 1, 4, 0, 2]);
    });
    it("Test ascending argsort unordered array", () => {
        expect(argsort([0, 1, 2, 3, 4, 5])).toEqual([0, 1, 2, 3, 4, 5]);
    });
    it("Test descending argsort unordered array", () => {
        expect(argsort([0, 1, 2, 3, 4, 5], false)).toEqual([5, 4, 3, 2, 1, 0]);
    });
    it("Test descending argsort ordered array", () => {
        expect(argsort([0, 4, 3, 2, 1, 5], false)).toEqual([5, 1, 2, 3, 4, 0]);
    });
});

// test sort matrix by index

describe("Sort matrix by index testing suite", function() {
    it("Test sort matrix ascending square", () => {
        expect(sort_matrix_by_index([1, 2, 3, 4], [2, 2], [10, 1])).toEqual([
            3,
            4,
            1,
            2
        ]);
    });

    it("Test sort matrix descending square", () => {
        expect(
            sort_matrix_by_index([1, 2, 3, 4], [2, 2], [10, 1], false)
        ).toEqual([1, 2, 3, 4]);
    });

    it("Test sort matrix ascending rectangular", () => {
        expect(
            sort_matrix_by_index([1, 2, 3, 4, 5, 6], [2, 3], [10, 1])
        ).toEqual([4, 5, 6, 1, 2, 3]);
    });

    it("Test sort matrix descending rectangular", () => {
        expect(
            sort_matrix_by_index([1, 2, 3, 4, 5, 6], [2, 3], [10, 1], false)
        ).toEqual([1, 2, 3, 4, 5, 6]);
    });
});

// test sort matrix by center column

describe("Test sort matrix by center testing suite", function() {
    it("Test sort matrix by center column ascending square", () => {
        expect(
            sort_matrix_by_center_column([1, 2, 3, 4], [2, 2], true)
        ).toEqual([1, 2, 3, 4]);
    });

    it("Test sort matrix by center column ascending rectangular", () => {
        expect(
            sort_matrix_by_center_column([1, 5, 3, 4, 2, 6], [2, 3], true)
        ).toEqual([4, 2, 6, 1, 5, 3]);
    });

    it("Test sort matrix by center column descending square", () => {
        expect(
            sort_matrix_by_center_column([1, 2, 3, 4], [2, 2], false)
        ).toEqual([3, 4, 1, 2]);
    });

    it("Test sort matrix by center column descending rectangular", () => {
        expect(
            sort_matrix_by_center_column([4, 2, 6, 1, 5, 3], [2, 3], false)
        ).toEqual([1, 5, 3, 4, 2, 6]);
    });
});

// test max array

describe("When max array is called", function() {
    it("Should return the maximum element of a sorted array", () => {
        expect(max_array([1, 2, 3, 4])).toEqual(4);
    });
    it("Should return the maximum element of an unsorted array", () => {
        expect(max_array([1, 4, 1, 2])).toEqual(4);
    });
    it("Should return the maximum element of an array that contains undefined", () => {
        expect(max_array([1, 4, undefined, 2])).toEqual(4);
    });
    it("Should return the maximum element of an array that contains infinite", () => {
        expect(max_array([1, 4, Infinity, 2])).toEqual(4);
    });
    it("Should return undefined if length of array is 0", () => {
        expect(max_array([])).toEqual(undefined);
    });
    it("Should return 0 from an array of all 0s", () => {
        expect(max_array([0,0,0])).toEqual(0);
    });
});

// test min array

describe("When min array is called", function() {
    it("Should return the max element of a sorted array", () => {
        expect(min_array([1, 2, 3, 4])).toEqual(1);
    });
    it("Should return the maximum element of an unsorted array", () => {
        expect(min_array([1, 4, 1, 2])).toEqual(1);
    });
    it("Should return the maximum element of an array that contains undefined", () => {
        expect(min_array([1, 4, undefined, 2])).toEqual(1);
    });
    it("Should return the maximum element of an array that contains infinite", () => {
        expect(min_array([1, 4, Infinity, 2])).toEqual(1);
    });
    it("Should return undefined if length of array is 0", () => {
        expect(min_array([])).toEqual(undefined);
    });
    it("Should return 0 from an array of all 0s", () => {
        expect(min_array([0,0,0])).toEqual(0);
    });
});

// test get percentile

describe("When get percentile is called", function() {
    it("Should return undefined if percentile is  < 0", () => {
        expect(getPercentile([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0], -1)).toEqual(undefined);
    });
    it("Should return undefined if percentile is  > 100", () => {
        expect(getPercentile([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0], 101)).toEqual(undefined);
    });
    it("Should return correct percentiles", () => {
        expect(getPercentile([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0], 0)).toBeCloseTo(0.0);
        expect(getPercentile([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0], 10)).toBeCloseTo(1.0);
        expect(getPercentile([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0], 20)).toBeCloseTo(2.0);
        expect(getPercentile([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0], 30)).toBeCloseTo(3.0);
        expect(getPercentile([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0], 40)).toBeCloseTo(4.0);
        expect(getPercentile([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0], 50)).toBeCloseTo(5.0);
        expect(getPercentile([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0], 60)).toBeCloseTo(6.0);
        expect(getPercentile([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0], 70)).toBeCloseTo(7.0);
        expect(getPercentile([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0], 80)).toBeCloseTo(8.0);
        expect(getPercentile([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0], 90)).toBeCloseTo(9.0);
        expect(getPercentile([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0], 100)).toBeCloseTo(10.0);
    });
});


// test normalize array

describe("When normalize lineProfile is called", function() {
    it("Should return a normalized array when called on integers", () => {
        expect(normalizeLineProfile([1, 2, 3, 4])).toBeDeepCloseTo([
            0,
            0.333333333333,
            0.6666666666666,
            1
        ]);
    });
    it("Should return a normalized array when called on floats", () => {
        expect(normalizeLineProfile([1, 2, 3, 4])).toBeDeepCloseTo([
            0,
            0.333333333333,
            0.6666666666666,
            1
        ]);
    });
    it("Should return a normalized array when called with an array containing undefined", () => {
        expect(
            normalizeLineProfile([1, 2, 3, 4, undefined])[4]
        ).not.toBeDefined();
        expect(
            normalizeLineProfile([1, 2, 3, 4, undefined]).slice(0, 4)
        ).toBeDeepCloseTo([0, 0.333333333333, 0.6666666666666, 1]);
    });
    it("Should return a normalized array when called with an array containing infinity", () => {
        expect(
            normalizeLineProfile([1, 2, 3, 4, Infinity])[4]
        ).not.toBeDefined();
        expect(
            normalizeLineProfile([1, 2, 3, 4, Infinity]).slice(0, 4)
        ).toBeDeepCloseTo([0, 0.333333333333, 0.6666666666666, 1]);
    });
    it("Should return a normalized array when all elements in the array are the same", () => {
        expect(normalizeLineProfile([2, 2, 2, 2])).toBeDeepCloseTo([
            1,
            1,
            1,
            1
        ]);
    });
});
