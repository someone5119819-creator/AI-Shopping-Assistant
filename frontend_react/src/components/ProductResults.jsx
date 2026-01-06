import React, { useState } from 'react';
import { ChevronDown, ChevronUp, ShoppingBag } from 'lucide-react';

export default function ProductResults({ products = [] }) {
    const [isExpanded, setIsExpanded] = useState(false);

    if (!products || products.length === 0) return null;

    return (
        <div className={`w-full bg-white rounded-3xl p-4 shadow-sm border border-gray-100 transition-all duration-300 ${isExpanded ? 'h-[60vh] overflow-y-auto' : 'h-auto'}`}>
            {/* Header */}
            <div
                className="flex items-center justify-between mb-4 cursor-pointer"
                onClick={() => setIsExpanded(!isExpanded)}
            >
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-blue-50 flex items-center justify-center">
                        <ShoppingBag className="w-4 h-4 text-blue-600" />
                    </div>
                    <span className="font-medium text-gray-800">Recommendations</span>
                    <span className="text-xs font-bold bg-gray-100 px-2 py-0.5 rounded-full text-gray-600">
                        {products.length}
                    </span>
                </div>
                <button className="text-gray-400 hover:text-gray-600">
                    {isExpanded ? <ChevronDown /> : <ChevronUp />}
                </button>
            </div>

            {/* Product List */}
            <div className={`grid gap-4 ${isExpanded ? 'grid-cols-1' : 'flex overflow-x-auto pb-2 snap-x'}`}>
                {products.map((product, index) => (
                    <div
                        key={index}
                        className={`flex-shrink-0 bg-white border border-gray-100 rounded-xl p-3 flex gap-4 ${isExpanded ? 'w-full' : 'w-[280px] snap-center'}`}
                    >
                        {/* Image Placeholder */}
                        <div className="w-20 h-20 bg-gray-50 rounded-lg flex-shrink-0 flex items-center justify-center">
                            {product.image ? (
                                <img src={product.image} alt={product.title} className="w-full h-full object-contain mix-blend-multiply" />
                            ) : (
                                <div className="text-2xl">📷</div>
                            )}
                        </div>

                        {/* Content */}
                        <div className="flex flex-col justify-center flex-1 min-w-0">
                            <h3 className="font-medium text-sm text-gray-900 line-clamp-2 leading-tight mb-1">
                                {product.title}
                            </h3>
                            <p className="text-lg font-bold text-gray-900">
                                {product.price}
                            </p>
                            {product.vendor && (
                                <p className="text-xs text-gray-500 mt-1">{product.vendor}</p>
                            )}
                        </div>
                    </div>
                ))}
            </div>

            {/* Footer Toggle (only if collapsed) */}
            {!isExpanded && (
                <button
                    onClick={() => setIsExpanded(true)}
                    className="w-full mt-3 py-2 text-xs font-medium text-gray-500 hover:text-gray-900 flex items-center justify-center gap-1 transition-colors"
                >
                    View all results <ChevronUp className="w-3 h-3" />
                </button>
            )}
        </div>
    );
}
