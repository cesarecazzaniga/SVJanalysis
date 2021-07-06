import awkward as ak


def divide_ak_arrays(ak_array1, ak_array2, division_by_zero_value=1., verbose=False):
    """Makes the division of an ak array by another one.
    
    The arrays ak_array1 and ak_array2 must have the same jagged structure.
    If division by zero for some indices, a default value to use can be
    defined, see examples.
    The output array has the same jagged structure as the input ak arrays.
    

    Args:
        ak_array1 (awkward.Array[float])
        ak_array2 (awkward.Array[float]) 
        division_by_zero_value (float, optional, default=1.)
        verbose (bool, optional, default=False)

    Returns:
        awkward.Array[float]: ak_array1 / ak_array2

    Examples:
        >>> ak_array1 = ak.Array([ [0, 3], [5], [1] ])
        >>> ak_array2 = ak.Array([ [3, 3], [0], [2] ])
        >>> divide_ak_arrays(ak_array1, ak_array2)
        [ [0, 1], [1], [0.5] ]
    """

    is_not_zero = (ak_array2!=0.)
    if (not ak.all(is_not_zero)) and verbose:
        print("The following warning about true_divide can be safely ignored.")

    raw_division = ak_array1/ak_array2
    division = ak.where(is_not_zero, raw_division, division_by_zero_value*ak.ones_like(ak_array1))

    # This implementation seems slower:
    #division = ak.Array([ [ x1/x2 if x2 != 0. else division_by_zero_value for x1, x2 in zip(y1, y2) ] for y1, y2 in zip(ak_array1, ak_a0rray2) ])

    return division


def is_in(ak_array, list_):
    """Check whether the elements of an ak array are in a list of elements.
    
    Args:
        ak_array1 (awkward.Array[T])
        list_ (list[T])

    Returns:
        awkward.Array[bool]

    Examples:
        >>> ak_array = ak.Array([ [11, 22, -11], [22], [111, 211, -11, 11] ])
        >>> list_ = [11, -11]
        >>> is_in(ak_array, list_)
        [[True, False, True], [False], [False, False, True, True]]
    """

    ak_bool = False * ak.ones_like(ak_array, dtype=bool)
    for el in list_:
        ak_bool = ak_bool | (ak_array == el)

    return ak_bool


def broadcast(ak_array1, ak_array2):
    """Broadcast arrays restricted to their common fields.

    Args:
        ak_array1 (awkward.Array)
        ak_array2 (awkward.Array)

    Returns:
        awkward.Array

    Example:
        >>> ak_array1 = ak.Array({"pt": [400, 300], "phi": [0.2, -0.5]})
        >>> ak_array2 = ak.Array({"pt": [[100, 30], [50, 20, 10]], "eta": [[-2, -1.9], [1.2, 1, 1.5]], "charge": [[1, -1], [1, 0, 0]]})
        >>> ak.to_list(akutl.broadcast(ak_array1, ak_array2))
        [[{'pt': [400, 400]}, {'pt': [300, 300, 300]}], [{'pt': [100, 30]}, {'pt': [50, 20, 10]}]]
    """

    fields1 = ak_array1.fields
    fields2 = ak_array2.fields
    if fields1 != fields2:
        common_fields = [ field for field in fields1 if field in fields2 ]
        ak_array1 = ak_array1[common_fields]
        ak_array2 = ak_array2[common_fields]

    return ak.broadcast_arrays(ak_array1, ak_array2)


def swap_axes(ak_array):
    """Swap the first two axes of a rectangular ak_array with two axes.

    It is possible that the whole array is copied into the memory, maing this
    function inefficient. No other good laternative was found.

    Args:
        ak_array (ak.Array)

    Returns:
        ak.Array
    """

    np_array = ak.to_numpy(ak_array)
    np_array = np_array.T
    ak_array = ak.Array([np_array])     # Can't avoid that copy in memory!!!
    return ak_array
