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
package com.github.kjburns.traffic_simulation.parameters;

import static org.junit.jupiter.api.Assertions.*;

import java.util.UUID;

import org.junit.jupiter.api.Test;

import com.github.kjburns.traffic_simulation.parameters.EmpiricalDistribution.Factory;
import com.github.kjburns.traffic_simulation.parameters.EmpiricalDistribution.Factory.Builder;

public class EmpiricalDistributionTest {
	private final Distribution<Double> testCompleteDistribution = createCompleteDistribution();
	private final Distribution<Double> testIncompleteDisribution = createIncompleteDistribution();

	private Distribution<Double> createCompleteDistribution() {
		final Builder builder = Factory.createBuilder("test", UUID.randomUUID());
		for (int i = 0; i <= 10; i++) {
			builder.addDataPoint(i / 10.0, i + 10.0);
		}
		final Distribution<Double> distr = builder.build();
		
		return distr;
	}
	
	private Distribution<Double> createIncompleteDistribution() {
		/*
		 * Only fills in from 0.2 to 0.8. It is expected that the gaps at the ends will be filled in.
		 */
		final Builder builder = Factory.createBuilder("test", UUID.randomUUID());
		for (int i = 2; i <= 8; i++) {
			builder.addDataPoint(i / 10.0, i + 10.0);
		}
		final Distribution<Double> distr = builder.build();
		
		return distr;
	}

	@Test void testParameterLimits0() {
		assertThrows(RuntimeException.class, () -> {
			testCompleteDistribution.getValue(-0.5);
		});
	}
	
	@Test void testParameterLimits1() {
		assertThrows(RuntimeException.class, () -> {
			testCompleteDistribution.getValue(1.5);
		});
	}
	
	@Test void testValue0() {
		double expected = 11.5;
		double actual = testCompleteDistribution.getValue(0.15);
		assertEquals(expected, actual, 0.001);
	}
	
	@Test void testValue1() {
		double expected = 15.6;
		double actual = testCompleteDistribution.getValue(0.56);
		assertEquals(expected, actual, 0.001);
	}
	
	@Test void testValue2() {
		double expected = 20.0;
		double actual = testCompleteDistribution.getValue(1.0);
		assertEquals(expected, actual, 0.001);
	}
	
	@Test void testIncompleteValue0() {
		double expected = 15.6;
		double actual = testIncompleteDisribution.getValue(0.56);
		assertEquals(expected, actual, 0.001);
	}
	
	@Test void testIncompleteValue1() {
		double expected = 18.0;
		double actual = testIncompleteDisribution.getValue(0.95);
		assertEquals(expected, actual, 0.001);
	}
	
	@Test void testIncompleteValue2() {
		double expected = 12.0;
		double actual = testIncompleteDisribution.getValue(0.15);
		assertEquals(expected, actual, 0.001);
	}
}
