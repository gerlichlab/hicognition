import {
    argsort,
    sort_matrix_by_index,
    sort_matrix_by_center_column
} from "../functions.js";

// test argsort
test("Test ascending argsort unordered array", () => {
    expect(argsort([4, 2, 6, 1, 3])).toEqual([3, 1, 4, 0, 2]);
});

test("Test ascending argsort ordered array", () => {
    expect(argsort([0, 1, 2, 3, 4, 5])).toEqual([0, 1, 2, 3, 4, 5]);
});

test("Test descending argsort unordered array", () => {
    expect(argsort([0, 1, 2, 3, 4, 5], false)).toEqual([5, 4, 3, 2, 1, 0]);
});

test("Test descending argsort ordered array", () => {
    expect(argsort([0, 4, 3, 2, 1, 5], false)).toEqual([5, 1, 2, 3, 4, 0]);
});

// test sort matrix by index

test("Test sort matrix ascending square", () => {
    expect(sort_matrix_by_index([1, 2, 3, 4], [2, 2], [10, 1])).toEqual([
        3,
        4,
        1,
        2
    ]);
});

test("Test sort matrix descending square", () => {
    expect(sort_matrix_by_index([1, 2, 3, 4], [2, 2], [10, 1], false)).toEqual([
        1,
        2,
        3,
        4
    ]);
});

test("Test sort matrix ascending rectangular", () => {
    expect(sort_matrix_by_index([1, 2, 3, 4, 5, 6], [2, 3], [10, 1])).toEqual([
        4,
        5,
        6,
        1,
        2,
        3
    ]);
});

test("Test sort matrix descending rectangular", () => {
    expect(
        sort_matrix_by_index([1, 2, 3, 4, 5, 6], [2, 3], [10, 1], false)
    ).toEqual([1, 2, 3, 4, 5, 6]);
});

// test sort matrix by center column

test("Test sort matrix by center column ascending square", () => {
    expect(sort_matrix_by_center_column([1, 2, 3, 4], [2, 2], true)).toEqual([
        1,
        2,
        3,
        4
    ]);
});

test("Test sort matrix by center column ascending rectangular", () => {
    expect(
        sort_matrix_by_center_column([1, 5, 3, 4, 2, 6], [2, 3], true)
    ).toEqual([4, 2, 6, 1, 5, 3]);
});

test("Test sort matrix by center column descending square", () => {
    expect(sort_matrix_by_center_column([1, 2, 3, 4], [2, 2], false)).toEqual([
        3,
        4,
        1,
        2
    ]);
});

test("Test sort matrix by center column descending rectangular", () => {
    expect(
        sort_matrix_by_center_column([4, 2, 6, 1, 5, 3], [2, 3], false)
    ).toEqual([1, 5, 3, 4, 2, 6]);
});
