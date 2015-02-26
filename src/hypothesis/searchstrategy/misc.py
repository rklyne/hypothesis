# coding=utf-8

# Copyright (C) 2013-2015 David R. MacIver (david@drmaciver.com)

# This file is part of Hypothesis (https://github.com/DRMacIver/hypothesis)

# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file, You can
# obtain one at http://mozilla.org/MPL/2.0/.

# END HEADER

from __future__ import division, print_function, absolute_import, \
    unicode_literals

from random import Random

import hypothesis.params as params
import hypothesis.descriptors as descriptors
import hypothesis.internal.distributions as dist
from hypothesis.types import RandomWithSeed
from hypothesis.internal.compat import integer_types
from hypothesis.internal.fixers import nice_string
from hypothesis.searchstrategy.strategy import BadData, SearchStrategy, \
    check_type, check_data_type

from .table import strategy_for, strategy_for_instances


class BoolStrategy(SearchStrategy):

    """A strategy that produces Booleans with a Bernoulli conditional
    distribution."""
    descriptor = bool
    size_lower_bound = 2
    size_upper_bound = 2

    parameter = params.UniformFloatParameter(0, 1)

    def produce_template(self, random, p):
        return dist.biased_coin(random, p)

    def to_basic(self, value):
        check_type(bool, value)
        return int(value)

    def from_basic(self, value):
        check_data_type(int, value)
        return bool(value)


class JustStrategy(SearchStrategy):

    """
    A strategy which simply returns a single fixed value with probability 1.
    """
    size_lower_bound = 1
    size_upper_bound = 1

    def __init__(self, value):
        SearchStrategy.__init__(self)
        self.descriptor = descriptors.Just(value)

    def __repr__(self):
        return 'JustStrategy(value=%r)' % (self.descriptor.value,)

    parameter = params.CompositeParameter()

    def produce_template(self, random, pv):
        return self.descriptor.value

    def to_basic(self, template):
        return None

    def from_basic(self, data):
        if data is not None:
            raise BadData('Expected None but got %s' % (nice_string(data,)))
        return self.descriptor.value


class RandomStrategy(SearchStrategy):

    """A strategy which produces Random objects.

    The conditional distribution is simply a RandomWithSeed seeded with
    a 128 bits of data chosen uniformly at random.

    """
    descriptor = Random
    parameter = params.CompositeParameter()

    def from_basic(self, data):
        check_data_type(integer_types, data)
        return data

    def to_basic(self, template):
        return template

    def produce_template(self, random, pv):
        return random.getrandbits(128)

    def reify(self, template):
        return RandomWithSeed(template)


class SampledFromStrategy(SearchStrategy):

    """A strategy which samples from a set of elements. This is essentially
    equivalent to using a OneOfStrategy over Just strategies but may be more
    efficient and convenient.

    The conditional distribution chooses uniformly at random from some
    non-empty subset of the elements.

    """

    def __init__(self, elements, descriptor=None):
        SearchStrategy.__init__(self)
        self.elements = tuple(elements)
        if descriptor is None:
            descriptor = descriptors.SampledFrom(self.elements)
        self.descriptor = descriptor
        self.parameter = params.NonEmptySubset(self.elements)
        try:
            s = set(self.elements)
            self.size_lower_bound = len(s)
            self.size_upper_bound = len(s)
        except TypeError:
            self.size_lower_bound = len(self.elements)
            self.size_upper_bound = len(self.elements)

    def to_basic(self, template):
        return template

    def from_basic(self, data):
        check_data_type(integer_types, data)
        if data < 0:
            raise BadData('Index out of range: %d < 0' % (data,))
        elif data >= len(self.elements):
            raise BadData(
                'Index out of range: %d >= %d' % (data, len(self.elements)))

        return data

    def produce_template(self, random, pv):
        return random.randint(0, len(self.elements) - 1)

    def reify(self, template):
        return self.elements[template]


strategy_for(bool)(BoolStrategy())


@strategy_for_instances(descriptors.Just)
def define_just_strategy(strategies, descriptor):
    return JustStrategy(descriptor.value)


@strategy_for_instances(SearchStrategy)
def define_strategy_strategy(strategies, descriptor):
    return descriptor


@strategy_for(Random)
def define_random_strategy(strategies, descriptor):
    return RandomStrategy()


@strategy_for_instances(descriptors.SampledFrom)
def define_sampled_strategy(strategies, descriptor):
    return SampledFromStrategy(descriptor.elements)


@strategy_for(None)
@strategy_for(type(None))
def define_none_strategy(strategies, descriptor):
    return JustStrategy(None)