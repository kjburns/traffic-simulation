/*
 * Copyright 2019 Kevin J. Burns, P.E.
 * Contact: kevin.burns.pe at gmail dot com
 * This file is part of Traffic Simulation.
 * 
 * Traffic Simulation is free software: you can redistribute it and/or modify 
 * it under the terms of the GNU Lesser General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * 
 * Traffic Simulation is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 * 
 * You should have received a copy of the GNU Lesser General Public License
 * along with Traffic Simulation.  If not, see <https://www.gnu.org/licenses/>.
 */
package com.github.kjburns.traffic_simulation.main;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

class UnitsEnumTest {
	@Test void testThatMetresAreIdentity() {
		final double distanceInMetres = 21;
		final double expected = 0.;
		final double actual = UnitsEnum.METRES.toMetres(distanceInMetres) - distanceInMetres;
		
		assertEquals(expected, actual, 0.000000001);
	}
	@Test void testThatMetersAndMetresAreEquivalent() {
		final double distanceInMeters = 34;
		final double expected = 0.;
		final double actual = UnitsEnum.METERS.toMetres(distanceInMeters) - distanceInMeters;
		
		assertEquals(expected, actual, 0.000000001);
	}
	
	@Test void testThatFeetAreProperlyDefined() {
		final double distanceInMetres = 0.3048;
		final double expected = 1.;
		final double actual = UnitsEnum.FEET.toThisUnit(distanceInMetres);
		
		assertEquals(expected, actual, 0.000000001);
	}
	
	@Test void testToThisUnit() {
		final double distanceInMetres = 1.;
		final double expected = 1. / 0.3048;
		final double actual = UnitsEnum.FEET.toThisUnit(distanceInMetres);
		
		assertEquals(expected, actual, 0.0001);
	}

	@Test void testToMetres() {
		final double distanceInFeet = 1.;
		final double expected = 0.3048; // metres
		final double actual = UnitsEnum.FEET.toMetres(distanceInFeet);
		
		assertEquals(expected, actual, 0.0001);
	}
}
