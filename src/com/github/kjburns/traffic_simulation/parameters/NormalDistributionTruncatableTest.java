package com.github.kjburns.traffic_simulation.parameters;

import static org.junit.jupiter.api.Assertions.*;

import java.util.UUID;

import org.junit.jupiter.api.Test;

import com.github.kjburns.traffic_simulation.parameters.NormalDistributionTruncatable.Factory.Options;

class NormalDistributionTruncatableTest {
	private final Distribution<Double> normalBell = NormalDistributionTruncatable.Factory.createDistribution(
			"test", UUID.randomUUID(), 3.0, 6.0, null);
	
	private final Options reverseBellOptions = createReverseBellOptions();
	private final Distribution<Double> reverseBell = NormalDistributionTruncatable.Factory.createDistribution(
			"test", UUID.randomUUID(), 3.0, 6.0, reverseBellOptions);
	
	private final Options truncatedBellOptions = createTruncatedBellOptions();
	private final Distribution<Double> truncatedBell = NormalDistributionTruncatable.Factory.createDistribution(
			"test", UUID.randomUUID(), 3.0, 6.0, truncatedBellOptions);
	
	@Test void testParameterLimits0() {
		assertThrows(RuntimeException.class, () -> {
			normalBell.getValue(-0.5);
		});
	}
	
	private Options createTruncatedBellOptions() {
		Options ret = new Options();
		ret.setMinValue(0.);
		ret.setMaxValue(10.);

		return ret;
	}

	private Options createReverseBellOptions() {
		Options ret = new Options();
		ret.setReverse(true);

		return ret;
	}

	@Test void testParameterLimits1() {
		assertThrows(RuntimeException.class, () -> {
			normalBell.getValue(1.5);
		});
	}
	
	@Test void testUntruncatedResult0() {
		double expected = 3.0;
		double actual = normalBell.getValue(0.5);
		assertEquals(expected, actual, 0.001);
	}
	
	@Test void testUntruncatedResult1() {
		double expected = -1.047;
		double actual = normalBell.getValue(0.25);
		assertEquals(expected, actual, 0.001);
	}
	
	@Test void testReversedResult() {
		double expected = 7.047;
		double actual = reverseBell.getValue(0.25);
		assertEquals(expected, actual, 0.001);
	}
	
	@Test void testTruncatedResult0() {
		double expected = 0.;
		double actual = truncatedBell.getValue(0.25);
		assertEquals(expected, actual, 0.001);
	}
	
	@Test void testTruncatedResult1() {
		double expected = 7.047;
		double actual = truncatedBell.getValue(0.75);
		assertEquals(expected, actual, 0.001);
	}
	
	@Test void testTruncatedResult2() {
		double expected = 10.;
		double actual = truncatedBell.getValue(0.9);
		assertEquals(expected, actual, 0.001);
	}
}
