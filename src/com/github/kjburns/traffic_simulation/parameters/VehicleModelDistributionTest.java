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

import java.io.InputStream;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;

import org.junit.jupiter.api.Test;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;

class VehicleModelDistributionTest {
	private final VehicleModelCollection models;
	private VehicleModelDistribution testDistribution;
	private final List<UUID> sortedUuids;

	public VehicleModelDistributionTest() throws Exception {
		try(final InputStream is = this.getClass().getClassLoader().getResourceAsStream(
				"res/VehicleModelTest.xml")) {
			final DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
			final DocumentBuilder db = dbf.newDocumentBuilder();
			final Document doc = db.parse(is);
			
			models = new VehicleModelCollectionImpl(doc.getDocumentElement());
		}
		try(final InputStream is = this.getClass().getClassLoader().getResourceAsStream(
				"res/VehicleModelDistributionTest.xml")) {
			final DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
			final DocumentBuilder db = dbf.newDocumentBuilder();
			final Document doc = db.parse(is);
			
			final NodeList nodes = doc.getDocumentElement().getElementsByTagName("distribution");
			testDistribution = new VehicleModelDistribution((Element)nodes.item(0), models);
		}
		
		sortedUuids = models.stream().map((item) -> {
			return item.getUuid();
		}).sorted(UUID::compareTo).collect(Collectors.toList());
	}
	
	@Test void checkParameterLimits0() {
		assertThrows(IllegalArgumentException.class, () -> {
			testDistribution.getValue(-0.1);
		});
	}
	
	@Test void checkParameterLimits1() {
		assertThrows(IllegalArgumentException.class, () -> {
			testDistribution.getValue(1.001);
		});
	}
	
	/*
	 * It is completely coincidental that the unit count in each model, which
	 * is the basis of comparison for easy coding sake, is in the order { 1, 2, 3 }.
	 * Sort order was found experimentally.
	 * The order is determined by java's sorting of UUID, which is voodoo-ey but likely 
	 * consistent. See here: http://anuff.com/2011/04/javautiluuidcompareto-considered-harmful/
	 * If Oracle changes this bug to something other than "won't fix" these tests will
	 * probably break.
	 */
	@Test void testValue0() {
		// occupies range [0, 0.85)
		final long expected = models.getByUuid(sortedUuids.get(0)).unitsStream().count();
		final long actual = testDistribution.getValue(0.5).unitsStream().count();
		
		assertEquals(expected, actual);
	}
	
	@Test void testValue1() {
		// occupies range [0.85, 0.95)
		final long expected = models.getByUuid(sortedUuids.get(1)).unitsStream().count();
		final long actual = testDistribution.getValue(0.9).unitsStream().count();
		
		assertEquals(expected, actual);
	}
	
	@Test void testValue2() {
		// occupies range [0.95, 1)
		final long expected = models.getByUuid(sortedUuids.get(2)).unitsStream().count();
		final long actual = testDistribution.getValue(0.96).unitsStream().count();
		
		assertEquals(expected, actual);
	}
}
