# -*- coding: utf-8 -*-
import math
import numpy as np


def get_tag(element):
    return element.tag.split('}')[-1]


def parse_string(element, prop):
    for p in element:
        if get_tag(p) == prop:
            return p.text
    return None


def parse_multilingual_text(element, prop):
    for p in element:
        if get_tag(p) == prop:
            result = dict()
            for multilingual_text in p:
                for localization in multilingual_text:
                    for localized_text in localization:
                        language = text = None
                        for item in localized_text:
                            if get_tag(item) == 'Language':
                                language = item.text
                            else:
                                text = item.text
                        if language and text:
                            result[language] = text
            return result
    return None


def parse_ref(element, prop):
    for p in element:
        if get_tag(p) == prop:
            return p.attrib['REF']
    return None


def parse_article_numbers(document_reference, tag):
    for element in document_reference:
        if get_tag(element) == tag:
            numbers = list()
            for number in element:
                numbers.append(number.text)
            if len(numbers) > 0:
                return '|'.join(numbers)
    return None


def get_angle(d_start, d_arc, d_end):
    circle = 2 * math.pi
    d_start_reduced = 0.0
    d_arc_reduced = d_arc - d_start
    d_end_reduced = d_end - d_start
    if d_arc_reduced < 0:
        d_arc_reduced += circle
    elif d_arc_reduced >= circle:
        d_arc_reduced -= circle
    if d_end_reduced < 0:
        d_end_reduced += circle
    elif d_end_reduced >= circle:
        d_end_reduced -= circle
    if d_start_reduced <= d_arc_reduced <= d_end_reduced:
        return d_end_reduced - d_start_reduced, 1
    else:
        return circle - d_end_reduced - d_start_reduced, -1


def stroke_arc(start, arc, end, max_diff, precision):

    # Calculate shift (x, y) to reduce coordinate values onto average coordinate
    sum_x = start[0] + arc[0] + end[0]
    sum_y = start[1] + arc[1] + end[1]
    shift = (sum_x / 3.0, sum_y / 3.0)

    # Reduce initial coordinates
    start_reduced = (start[0] - shift[0], start[1] - shift[1])
    arc_reduced = (arc[0] - shift[0], arc[1] - shift[1])
    end_reduced = (end[0] - shift[0], end[1] - shift[1])

    # Calculate circle radius and center point
    les1 = np.array([
        [-1, start_reduced[0], start_reduced[1]],
        [-1, arc_reduced[0], arc_reduced[1]],
        [-1, end_reduced[0], end_reduced[1]]
    ])
    les2 = np.array([
        math.pow(start_reduced[0], 2) + math.pow(start_reduced[1], 2),
        math.pow(arc_reduced[0], 2) + math.pow(arc_reduced[1], 2),
        math.pow(end_reduced[0], 2) + math.pow(end_reduced[1], 2)
    ])
    a, b, c = np.linalg.solve(les1, les2)
    m = (b/2., c/2.)
    r = math.sqrt(math.pow(m[0], 2) + math.pow(m[1], 2) - a)

    # Calculate maximum angle step size
    max_delta_alpha = 2 * math.acos(1 - max_diff/r)

    # Calculate number of points needed to approximate the arc
    dx = end_reduced[0] - start_reduced[0]
    dy = end_reduced[1] - start_reduced[1]
    dist_start_end = math.sqrt(math.pow(dx, 2) + math.pow(dy, 2))
    diff_alpha = 2 * math.asin(dist_start_end / (2 * r))
    num_points = math.ceil(diff_alpha / max_delta_alpha)

    # Calculate directions
    d_start = math.atan2(start_reduced[1] - m[1], start_reduced[0] - m[0])
    d_arc = math.atan2(arc_reduced[1] - m[1], arc_reduced[0] - m[0])
    d_end = math.atan2(end_reduced[1] - m[1], end_reduced[0] - m[0])

    # Determine angle and rotation direction
    d_diff, rot = get_angle(d_start, d_arc, d_end)

    # Calculate points
    coords = list()
    d_step = d_diff / num_points
    for i in range(1, int(num_points) + 1, 1):
        x = m[0] + r * math.cos(d_start + d_step * i * rot) + shift[0]
        y = m[1] + r * math.sin(d_start + d_step * i * rot) + shift[1]
        coords.append((round(x, precision), round(y, precision)))

    # Remove duplicate points
    if len(coords) > 1:
        duplicates = list()
        for i in range(1, len(coords)):
            if coords[i][0] == coords[i - 1][0] and coords[i][1] == coords[i - 1][1]:
                duplicates.append(i)
        duplicates.reverse()
        for duplicate in duplicates:
            coords.pop(duplicate)

    # Return coordinates
    return coords
