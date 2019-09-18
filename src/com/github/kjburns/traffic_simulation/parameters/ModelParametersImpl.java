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

import java.io.IOException;
import java.io.InputStream;
import java.util.HashMap;
import java.util.Map;
import javax.xml.parsers.ParserConfigurationException;

import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.NodeList;
import org.xml.sax.SAXException;

import com.github.kjburns.traffic_simulation.main.ProjectInputStreamProvider;
import com.github.kjburns.traffic_simulation.xml.ValidatingDocumentLoader;

public class ModelParametersImpl implements ModelParameters {
	private interface CollectionLoader {
		void loadCollection(Element from);
	}
	
	private static final String TYPE_ATTR = "type";
	private static final String DISTRIBUTIONS_XSD_PATH = 
			"https://raw.githubusercontent.com/kjburns/traffic-simulation/develop/xml/distributions.xsd";
	private static final String VEHICLE_TYPE_XSD_PATH =
			"https://raw.githubusercontent.com/kjburns/traffic-simulation/develop/xml/vehicle-models.xsd";
	private static final String DISTRIBUTION_SET_TAG = "distribution-set";
	private final Map<String, CollectionLoader> collectionLoaders = defineCollectionLoaders();
	
	/*
	 * Add distribution set instances here
	 */
	private ConnectorLinkSelectionBehaviorDistributionCollection connectorLinkSelectionBehaviors = null;
	private ConnectorMaxPositioningDistanceDistributionCollection connectorMaxPositioningDistances = null;
	private VehicleModelCollection vehicleModels = null;

	public ModelParametersImpl(ProjectInputStreamProvider isProvider) throws ParserConfigurationException, SAXException, IOException {
		try(final InputStream vehicleModelsStream = isProvider.createInputStreamForVehicleModels()) {
			Document doc = ValidatingDocumentLoader.loadDocument(vehicleModelsStream, VEHICLE_TYPE_XSD_PATH);
			
			final Element docElement = doc.getDocumentElement();
			
			vehicleModels = new VehicleModelCollectionImpl(docElement);
		}

		try(final InputStream distributionsStream = isProvider.createInputStreamForDistributions()) {
			Document doc = ValidatingDocumentLoader.loadDocument(distributionsStream, DISTRIBUTIONS_XSD_PATH);
			
			final Element docElement = doc.getDocumentElement();
			final NodeList elements = docElement.getElementsByTagName(DISTRIBUTION_SET_TAG);
			for (int i = 0; i < elements.getLength(); i++) {
				Element e = (Element)elements.item(i);
				String type = e.getAttribute(ModelParametersImpl.TYPE_ATTR);
				final CollectionLoader loader = collectionLoaders.get(type);
				if (loader != null) {
					loader.loadCollection(e);
				} else {
					System.err.println("Error: Could not find loader for " + type);
				}
			}
		}
		
		testLatestFeature();
	}
	
	private void testLatestFeature() {
		vehicleModels.stream().forEach((item) -> {
			System.out.println(item.getName());
			System.out.print("Total Length: ");
			System.out.println(item.getTotalLength());
			System.out.println();
		});
	}

	private Map<String, CollectionLoader> defineCollectionLoaders() {
		Map<String, CollectionLoader> ret = new HashMap<>();
		ret.put(ConnectorLinkSelectionBehaviorDistributionCollection.DISTRIBUTION_TYPE_VALUE, (from) -> {
			connectorLinkSelectionBehaviors = 
					new ConnectorLinkSelectionBehaviorDistributionCollection(from);
		});
		ret.put(ConnectorMaxPositioningDistanceDistributionCollection.DISTRIBUTION_TYPE_VALUE, (from) -> {
			connectorMaxPositioningDistances =
					new ConnectorMaxPositioningDistanceDistributionCollection(from);
		});

		/*
		 * Add new distribution set loaders above this comment
		 */

		return ret;
	}

	@Override
	public DistributionCollection<ConnectorLinkSelectionBehaviorEnum> getConnectorLinkSelectionBehaviors() {
		return connectorLinkSelectionBehaviors;
	}

	@Override
	public DistributionCollection<Double> getConnectorMaxPositioningDistances() {
		return connectorMaxPositioningDistances;
	}

	@Override
	public VehicleModelCollection getVehicleModels() {
		return vehicleModels;
	}
}
